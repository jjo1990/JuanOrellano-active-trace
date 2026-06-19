import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fecha_academica import FechaAcademica
from app.repositories.base import Repository


class FechaAcademicaRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo: Repository[FechaAcademica] = Repository(session, tenant_id, FechaAcademica)
        self._session = session

    async def create(self, entity: FechaAcademica) -> FechaAcademica:
        return await self._repo.create(entity)

    async def get(self, id: uuid.UUID) -> FechaAcademica | None:
        return await self._repo.get(id)

    async def list_with_filters(self, **filters) -> Sequence[FechaAcademica]:
        return await self._repo.list(**filters)

    async def list_by_cohorte(self, cohorte_id: uuid.UUID) -> Sequence[FechaAcademica]:
        stmt = (
            select(FechaAcademica)
            .where(
                FechaAcademica.tenant_id == self._repo._tenant_id,
                FechaAcademica.cohorte_id == cohorte_id,
                FechaAcademica.deleted_at.is_(None),
            )
            .order_by(FechaAcademica.fecha.asc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update(self, entity: FechaAcademica) -> FechaAcademica:
        return await self._repo.update(entity)

    async def soft_delete(self, id: uuid.UUID) -> None:
        await self._repo.soft_delete(id)
