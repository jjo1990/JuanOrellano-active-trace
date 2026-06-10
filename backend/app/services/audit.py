import uuid
from datetime import datetime

from fastapi import Request

from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository


class AuditService:
    def __init__(self, repository: AuditLogRepository) -> None:
        self._repo = repository

    async def log(
        self,
        actor_id: uuid.UUID,
        tenant_id: uuid.UUID,
        accion: str,
        detalle: dict | None = None,
        filas_afectadas: int = 0,
        request: Request | None = None,
        impersonado_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
    ) -> AuditLog:
        ip = request.client.host if request and request.client else None
        user_agent = request.headers.get("user-agent") if request else None
        record = AuditLog(
            actor_id=actor_id,
            tenant_id=tenant_id,
            accion=accion,
            detalle=detalle,
            filas_afectadas=filas_afectadas,
            ip=ip,
            user_agent=user_agent,
            impersonado_id=impersonado_id,
            materia_id=materia_id,
            fecha_hora=datetime.now(),
        )
        return await self._repo.create(record)
