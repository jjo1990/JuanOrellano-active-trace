import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron
from app.repositories.base import Repository


class PadronRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._version_repo: Repository[VersionPadron] = Repository(session, tenant_id, VersionPadron)
        self._entrada_repo: Repository[EntradaPadron] = Repository(session, tenant_id, EntradaPadron)

    async def get_active_version(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> VersionPadron | None:
        stmt = (
            select(VersionPadron)
            .where(
                VersionPadron.materia_id == materia_id,
                VersionPadron.cohorte_id == cohorte_id,
                VersionPadron.tenant_id == self._tenant_id,
                VersionPadron.activa.is_(True),
                VersionPadron.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_version(self, entity: VersionPadron) -> VersionPadron:
        active = await self.get_active_version(entity.materia_id, entity.cohorte_id)
        if active:
            active.activa = False
            merged = await self._session.merge(active)
            await self._session.flush()
        return await self._version_repo.create(entity)

    async def get_version(self, id: uuid.UUID) -> VersionPadron | None:
        return await self._version_repo.get(id)

    async def get_entradas_activas_por_materia(
        self, materia_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        stmt = (
            select(EntradaPadron)
            .join(VersionPadron, VersionPadron.id == EntradaPadron.version_id)
            .where(
                VersionPadron.materia_id == materia_id,
                VersionPadron.activa.is_(True),
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
                VersionPadron.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_versions(
        self, materia_id: uuid.UUID | None = None,
    ) -> Sequence[VersionPadron]:
        filters: dict = {}
        if materia_id is not None:
            filters["materia_id"] = materia_id
        return await self._version_repo.list(**filters)

    async def create_entrada(self, entity: EntradaPadron) -> EntradaPadron:
        return await self._entrada_repo.create(entity)

    async def create_entradas_batch(
        self, entradas: list[EntradaPadron],
    ) -> list[EntradaPadron]:
        results = []
        for e in entradas:
            r = await self._entrada_repo.create(e)
            results.append(r)
        return results

    async def list_entradas(
        self, version_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        return await self._entrada_repo.list(version_id=version_id)

    async def count_entradas(self, version_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(EntradaPadron)
            .where(
                EntradaPadron.version_id == version_id,
                EntradaPadron.tenant_id == self._tenant_id,
                EntradaPadron.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def soft_delete_by_materia(self, materia_id: uuid.UUID) -> int:
        versions = await self.list_versions(materia_id=materia_id)
        total = 0
        for v in versions:
            stmt_entradas = (
                sa_update(EntradaPadron)
                .where(
                    EntradaPadron.version_id == v.id,
                    EntradaPadron.tenant_id == self._tenant_id,
                    EntradaPadron.deleted_at.is_(None),
                )
                .values(deleted_at=func.now())
            )
            result_e = await self._session.execute(stmt_entradas)
            total += result_e.rowcount

            stmt_v = (
                sa_update(VersionPadron)
                .where(
                    VersionPadron.id == v.id,
                    VersionPadron.tenant_id == self._tenant_id,
                    VersionPadron.deleted_at.is_(None),
                )
                .values(deleted_at=func.now())
            )
            result_v = await self._session.execute(stmt_v)
            total += result_v.rowcount
        return total
