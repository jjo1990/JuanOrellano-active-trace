import uuid

from fastapi import HTTPException, Request

from app.core import action_codes
from app.core.security import create_access_token, verify_access_token
from app.repositories.user_repository import UserRepository
from app.services.audit import AuditService


class ImpersonationService:
    def __init__(
        self,
        user_repo: UserRepository,
        audit_service: AuditService,
    ) -> None:
        self._user_repo = user_repo
        self._audit = audit_service

    async def start_impersonation(
        self,
        actor_user_id: uuid.UUID,
        target_user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        request: Request,
    ) -> str:
        target = await self._user_repo.get(target_user_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        token = create_access_token(
            user_id=target_user_id,
            tenant_id=tenant_id,
            extra_claims={
                "impersonating": True,
                "actor_id": str(actor_user_id),
            },
        )

        await self._audit.log(
            actor_id=actor_user_id,
            tenant_id=tenant_id,
            accion=action_codes.IMPERSONACION_INICIAR,
            impersonado_id=target_user_id,
            request=request,
        )

        return token

    async def stop_impersonation(
        self,
        current_user_id: uuid.UUID,
        actor_id: uuid.UUID | None,
        tenant_id: uuid.UUID,
        request: Request,
    ) -> str:
        if actor_id is None or actor_id == current_user_id:
            raise HTTPException(
                status_code=400,
                detail="No hay impersonación activa.",
            )

        token = create_access_token(
            user_id=actor_id,
            tenant_id=tenant_id,
        )

        await self._audit.log(
            actor_id=actor_id,
            tenant_id=tenant_id,
            accion=action_codes.IMPERSONACION_FINALIZAR,
            impersonado_id=current_user_id,
            request=request,
        )

        return token
