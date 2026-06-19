import logging
import uuid
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.programa_materia import ProgramaMateria
from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.schemas.programa import ProgramaCreateRequest, ProgramaUpdateRequest

logger = logging.getLogger(__name__)


class ProgramaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = ProgramaMateriaRepository(session, tenant_id)
        self._session = session

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(status_code=409, detail="El recurso ya existe o viola una restriccion de unicidad.") from exc

    async def _run(self, coro):
        try:
            result = await coro
            return result
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(status_code=409, detail="El recurso ya existe o viola una restriccion de unicidad.") from exc

    async def create(self, data: ProgramaCreateRequest) -> ProgramaMateria:
        entity = ProgramaMateria(
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            titulo=data.titulo,
            referencia_archivo=data.referencia_archivo,
        )
        result = await self._run(self._repo.create(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def get(self, id: uuid.UUID) -> ProgramaMateria | None:
        return await self._repo.get(id)

    async def list_all(self, **filters) -> Sequence[ProgramaMateria]:
        return await self._repo.list_all(**filters)

    async def update(self, id: uuid.UUID, data: ProgramaUpdateRequest) -> ProgramaMateria:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Programa no encontrado.")
        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def delete(self, id: uuid.UUID) -> None:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Programa no encontrado.")
        await self._run(self._repo.soft_delete(id))
        await self._commit()
