import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programa_materia import ProgramaMateria
from app.repositories.base import Repository


class ProgramaMateriaRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo: Repository[ProgramaMateria] = Repository(session, tenant_id, ProgramaMateria)
        self._session = session

    async def create(self, entity: ProgramaMateria) -> ProgramaMateria:
        return await self._repo.create(entity)

    async def get(self, id: uuid.UUID) -> ProgramaMateria | None:
        return await self._repo.get(id)

    async def list_all(self, **filters) -> Sequence[ProgramaMateria]:
        return await self._repo.list(**filters)

    async def update(self, entity: ProgramaMateria) -> ProgramaMateria:
        return await self._repo.update(entity)

    async def soft_delete(self, id: uuid.UUID) -> None:
        await self._repo.soft_delete(id)
