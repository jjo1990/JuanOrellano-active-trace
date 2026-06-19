import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.perfil import PerfilResponse, PerfilUpdate

logger = logging.getLogger(__name__)


class PerfilService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = UserRepository(session, tenant_id)
        self._session = session
        self._tenant_id = tenant_id

    def _entity_to_response(self, entity: User) -> PerfilResponse:
        return PerfilResponse(
            id=entity.id,
            tenant_id=entity.tenant_id,
            nombre=entity.nombre,
            apellidos=entity.apellidos,
            email=entity.email,
            dni=entity.dni,
            cuil=entity.cuil,
            cbu=entity.cbu,
            alias_cbu=entity.alias_cbu,
            banco=entity.banco,
            regional=entity.regional,
            legajo=entity.legajo,
            legajo_profesional=entity.legajo_profesional,
            facturador=entity.facturador,
            activo=entity.activo,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_perfil(self, user_id: uuid.UUID) -> PerfilResponse:
        entity = await self._repo.get(user_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return self._entity_to_response(entity)

    async def update_perfil(
        self, user_id: uuid.UUID, data: PerfilUpdate,
    ) -> PerfilResponse:
        entity = await self._repo.get(user_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(entity, field):
                setattr(entity, field, value)

        try:
            merged = await self._repo.update(entity)
            await self._session.commit()
            await self._session.refresh(merged)
            return self._entity_to_response(merged)
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError en update_perfil: %s", exc)
            raise HTTPException(
                status_code=409,
                detail="El email ya está en uso por otro usuario en este tenant.",
            ) from exc
