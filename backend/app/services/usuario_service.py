import logging
import uuid
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioStatusUpdate,
    UsuarioUpdate,
)

logger = logging.getLogger(__name__)


class UsuarioService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = UserRepository(session, tenant_id)
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

    def _entity_to_response(self, entity: User) -> UsuarioResponse:
        return UsuarioResponse(
            id=entity.id,
            tenant_id=entity.tenant_id,
            nombre=entity.nombre,
            apellidos=entity.apellidos,
            email=entity.email,
            banco=entity.banco,
            regional=entity.regional,
            legajo=entity.legajo,
            legajo_profesional=entity.legajo_profesional,
            facturador=entity.facturador,
            activo=entity.activo,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, data: UsuarioCreate) -> UsuarioResponse:
        entity = User(
            nombre=data.nombre,
            apellidos=data.apellidos,
            email=data.email,
            password_hash=hash_password(data.password),
            dni=data.dni,
            cuil=data.cuil,
            cbu=data.cbu,
            alias_cbu=data.alias_cbu,
            banco=data.banco,
            regional=data.regional,
            legajo=data.legajo,
            legajo_profesional=data.legajo_profesional,
            facturador=data.facturador,
            activo=data.activo,
        )
        result = await self._run(self._repo.create(entity))
        await self._commit()
        await self._session.refresh(result)
        return self._entity_to_response(result)

    async def update(self, id: uuid.UUID, data: UsuarioUpdate) -> UsuarioResponse:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        update_dict = data.model_dump(exclude_unset=True)
        password = update_dict.pop("password", None)
        if password is not None:
            entity.password_hash = hash_password(password)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update(entity))
        await self._commit()
        await self._session.refresh(result)
        return self._entity_to_response(result)

    async def get(self, id: uuid.UUID) -> UsuarioResponse:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return self._entity_to_response(entity)

    async def list(
        self,
        activo: bool | None = None,
        q: str | None = None,
    ) -> Sequence[UsuarioResponse]:
        if q is not None:
            entities = await self._repo.search_by_name(q)
        elif activo is not None:
            entities = await self._repo.filter_by_active(activo)
        else:
            entities = await self._repo.list_by_tenant()
        return [self._entity_to_response(e) for e in entities]

    async def update_status(
        self, id: uuid.UUID, data: UsuarioStatusUpdate,
    ) -> UsuarioResponse:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        entity.activo = data.activo
        result = await self._run(self._repo.update(entity))
        await self._commit()
        await self._session.refresh(result)
        return self._entity_to_response(result)
