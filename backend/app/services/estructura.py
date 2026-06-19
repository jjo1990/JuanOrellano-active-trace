import logging
import uuid
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.repositories.estructura import EstructuraRepository
from app.schemas.estructura import (
    CarreraCreate,
    CarreraUpdate,
    CohorteCreate,
    CohorteUpdate,
    MateriaCreate,
    MateriaUpdate,
)

logger = logging.getLogger(__name__)


class EstructuraService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = EstructuraRepository(session, tenant_id)
        self._session = session

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(status_code=409, detail="El recurso ya existe o viola una restricción de unicidad.") from exc

    async def _run(self, coro):
        try:
            result = await coro
            return result
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(status_code=409, detail="El recurso ya existe o viola una restricción de unicidad.") from exc

    # ── Carrera ───────────────────────────────────────────────────────────

    async def create_carrera(self, data: CarreraCreate) -> Carrera:
        entity = Carrera(codigo=data.codigo, nombre=data.nombre, activa=data.activa)
        result = await self._run(self._repo.create_carrera(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def get_carrera(self, id: uuid.UUID) -> Carrera | None:
        return await self._repo.get_carrera(id)

    async def list_carreras(self) -> Sequence[Carrera]:
        return await self._repo.list_carreras()

    async def update_carrera(self, id: uuid.UUID, data: CarreraUpdate) -> Carrera:
        entity = await self._repo.get_carrera(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Carrera no encontrada.")
        update_dict = data.model_dump(exclude_unset=True)
        if "activa" in update_dict and not update_dict["activa"]:
            cohortes_activas = await self._repo.list_cohortes(carrera_id=id, activa=True)
            if cohortes_activas:
                raise HTTPException(
                    status_code=409,
                    detail="No se puede inactivar una carrera con cohortes activas. Debe cerrar las cohortes primero.",
                )
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update_carrera(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def delete_carrera(self, id: uuid.UUID) -> None:
        entity = await self._repo.get_carrera(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Carrera no encontrada.")
        await self._run(self._repo.soft_delete_carrera(id))
        await self._commit()

    # ── Cohorte ───────────────────────────────────────────────────────────

    async def _ensure_carrera_activa(self, carrera_id: uuid.UUID) -> Carrera:
        carrera = await self._repo.get_carrera(carrera_id)
        if carrera is None:
            raise HTTPException(status_code=404, detail="Carrera no encontrada.")
        if not carrera.activa:
            raise HTTPException(
                status_code=409,
                detail="No se puede crear una cohorte activa para una carrera inactiva.",
            )
        return carrera

    async def create_cohorte(self, data: CohorteCreate) -> Cohorte:
        if data.activa:
            await self._ensure_carrera_activa(data.carrera_id)
        entity = Cohorte(
            carrera_id=data.carrera_id,
            nombre=data.nombre,
            anio=data.anio,
            vig_desde=data.vig_desde,
            vig_hasta=data.vig_hasta,
            activa=data.activa,
        )
        result = await self._run(self._repo.create_cohorte(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def get_cohorte(self, id: uuid.UUID) -> Cohorte | None:
        return await self._repo.get_cohorte(id)

    async def list_cohortes(self) -> Sequence[Cohorte]:
        return await self._repo.list_cohortes()

    async def update_cohorte(self, id: uuid.UUID, data: CohorteUpdate) -> Cohorte:
        entity = await self._repo.get_cohorte(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Cohorte no encontrada.")
        update_dict = data.model_dump(exclude_unset=True)
        if update_dict.get("activa") is True:
            carrera_id = update_dict.get("carrera_id", entity.carrera_id)
            await self._ensure_carrera_activa(carrera_id)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update_cohorte(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def delete_cohorte(self, id: uuid.UUID) -> None:
        entity = await self._repo.get_cohorte(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Cohorte no encontrada.")
        await self._run(self._repo.soft_delete_cohorte(id))
        await self._commit()

    # ── Materia ───────────────────────────────────────────────────────────

    async def create_materia(self, data: MateriaCreate) -> Materia:
        entity = Materia(
            codigo=data.codigo, nombre=data.nombre, activa=data.activa,
            grupo_plus=data.grupo_plus,
        )
        result = await self._run(self._repo.create_materia(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def get_materia(self, id: uuid.UUID) -> Materia | None:
        return await self._repo.get_materia(id)

    async def list_materias(self) -> Sequence[Materia]:
        return await self._repo.list_materias()

    async def update_materia(self, id: uuid.UUID, data: MateriaUpdate) -> Materia:
        entity = await self._repo.get_materia(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Materia no encontrada.")
        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update_materia(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def delete_materia(self, id: uuid.UUID) -> None:
        entity = await self._repo.get_materia(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Materia no encontrada.")
        await self._run(self._repo.soft_delete_materia(id))
        await self._commit()
