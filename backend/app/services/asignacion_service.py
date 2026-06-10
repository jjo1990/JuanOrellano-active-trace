import logging
import uuid
from datetime import date
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.repositories.asignacion_repository import AsignacionRepository
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionResponse,
    AsignacionUpdate,
)

logger = logging.getLogger(__name__)


class AsignacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = AsignacionRepository(session, tenant_id)
        self._session = session
        self._tenant_id = tenant_id

    async def _run(self, coro):
        try:
            result = await coro
            return result
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409,
                detail="El recurso ya existe o viola una restricción de unicidad.",
            ) from exc

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409,
                detail="El recurso ya existe o viola una restricción de unicidad.",
            ) from exc

    async def _validate_fk(
        self, model_class, entity_id: uuid.UUID | None, label: str,
    ) -> None:
        if entity_id is None:
            return
        stmt = (
            select(model_class)
            .where(
                model_class.id == entity_id,
                model_class.tenant_id == self._tenant_id,
            )
        )
        result = await self._session.execute(stmt)
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=404,
                detail=f"{label} no encontrada(o) en este tenant.",
            )

    async def _validate_fks(self, data: AsignacionCreate | AsignacionUpdate) -> None:
        fields = [
            (User, "usuario_id", "Usuario"),
            (Rol, "rol_id", "Rol"),
            (Materia, "materia_id", "Materia"),
            (Carrera, "carrera_id", "Carrera"),
            (Cohorte, "cohorte_id", "Cohorte"),
        ]
        for model_class, field_name, label in fields:
            fk_id = getattr(data, field_name, None)
            if fk_id is not None:
                await self._validate_fk(model_class, fk_id, label)

    @staticmethod
    def is_vigente(asignacion: Asignacion) -> bool:
        hoy = date.today()
        if asignacion.desde > hoy:
            return False
        if asignacion.hasta is not None and asignacion.hasta < hoy:
            return False
        return True

    def _entity_to_response(self, entity: Asignacion) -> AsignacionResponse:
        return AsignacionResponse(
            id=entity.id,
            tenant_id=entity.tenant_id,
            usuario_id=entity.usuario_id,
            rol_id=entity.rol_id,
            materia_id=entity.materia_id,
            carrera_id=entity.carrera_id,
            cohorte_id=entity.cohorte_id,
            comisiones=entity.comisiones,
            responsable_id=entity.responsable_id,
            desde=entity.desde,
            hasta=entity.hasta,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, data: AsignacionCreate) -> AsignacionResponse:
        if data.hasta is not None and data.hasta < data.desde:
            raise HTTPException(
                status_code=400,
                detail="La fecha 'hasta' debe ser posterior o igual a 'desde'.",
            )
        await self._validate_fks(data)
        entity = Asignacion(
            usuario_id=data.usuario_id,
            rol_id=data.rol_id,
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            comisiones=data.comisiones,
            responsable_id=data.responsable_id,
            desde=data.desde,
            hasta=data.hasta,
        )
        result = await self._run(self._repo.create(entity))
        await self._commit()
        await self._session.refresh(result)
        return self._entity_to_response(result)

    async def update(
        self, id: uuid.UUID, data: AsignacionUpdate,
    ) -> AsignacionResponse:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Asignación no encontrada.")
        update_dict = data.model_dump(exclude_unset=True)
        if "usuario_id" in update_dict:
            del update_dict["usuario_id"]
        if "tenant_id" in update_dict:
            del update_dict["tenant_id"]
        if update_dict.get("desde") and update_dict.get("hasta"):
            if update_dict["hasta"] < update_dict["desde"]:
                raise HTTPException(
                    status_code=400,
                    detail="La fecha 'hasta' debe ser posterior o igual a 'desde'.",
                )
        await self._validate_fks(data)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update(entity))
        await self._commit()
        await self._session.refresh(result)
        return self._entity_to_response(result)

    async def get(self, id: uuid.UUID) -> AsignacionResponse:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Asignación no encontrada.")
        return self._entity_to_response(entity)

    async def soft_delete(self, id: uuid.UUID) -> None:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Asignación no encontrada.")
        await self._run(self._repo.soft_delete(id))
        await self._commit()

    async def list(
        self,
        usuario_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        rol_id: uuid.UUID | None = None,
        vigente: bool | None = None,
    ) -> Sequence[AsignacionResponse]:
        entities = await self._repo.filter_by_context(
            usuario_id=usuario_id,
            materia_id=materia_id,
            rol_id=rol_id,
            vigente=vigente,
        )
        return [self._entity_to_response(e) for e in entities]
