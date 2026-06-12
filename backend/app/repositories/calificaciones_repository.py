import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.umbral_materia import UmbralMateria
from app.repositories.base import Repository


class CalificacionesRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._cal_repo: Repository[Calificacion] = Repository(session, tenant_id, Calificacion)
        self._umbral_repo: Repository[UmbralMateria] = Repository(session, tenant_id, UmbralMateria)

    async def create_calificacion(self, entity: Calificacion) -> Calificacion:
        return await self._cal_repo.create(entity)

    async def create_calificaciones_batch(self, entradas: list[Calificacion]) -> list[Calificacion]:
        for e in entradas:
            e.tenant_id = self._tenant_id
            self._session.add(e)
        await self._session.flush()
        return entradas

    async def get_calificaciones_by_entrada(self, entrada_padron_id: uuid.UUID) -> Sequence[Calificacion]:
        return await self._cal_repo.list(entrada_padron_id=entrada_padron_id)

    async def get_calificaciones_by_materia(self, materia_id: uuid.UUID) -> Sequence[Calificacion]:
        return await self._cal_repo.list(materia_id=materia_id)

    async def count_calificaciones(self, materia_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Calificacion)
            .where(
                Calificacion.materia_id == materia_id,
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def soft_delete_by_materia(self, materia_id: uuid.UUID) -> int:
        stmt = (
            sa_update(Calificacion)
            .where(
                Calificacion.materia_id == materia_id,
                Calificacion.tenant_id == self._tenant_id,
                Calificacion.deleted_at.is_(None),
            )
            .values(deleted_at=func.now())
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def get_umbral(self, materia_id: uuid.UUID, asignacion_id: uuid.UUID) -> UmbralMateria | None:
        stmt = (
            select(UmbralMateria)
            .where(
                UmbralMateria.asignacion_id == asignacion_id,
                UmbralMateria.materia_id == materia_id,
                UmbralMateria.tenant_id == self._tenant_id,
                UmbralMateria.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_umbral_by_materia(self, materia_id: uuid.UUID) -> UmbralMateria | None:
        stmt = (
            select(UmbralMateria)
            .where(
                UmbralMateria.materia_id == materia_id,
                UmbralMateria.tenant_id == self._tenant_id,
                UmbralMateria.deleted_at.is_(None),
            )
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_umbral(self, entity: UmbralMateria) -> UmbralMateria:
        existing = await self.get_umbral(entity.materia_id, entity.asignacion_id)
        if existing is not None:
            existing.umbral_pct = entity.umbral_pct
            existing.valores_aprobatorios = entity.valores_aprobatorios
            merged = await self._session.merge(existing)
            await self._session.flush()
            return merged
        return await self._umbral_repo.create(entity)
