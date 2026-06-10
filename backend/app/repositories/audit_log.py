import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        self._session.add(audit_log)
        await self._session.flush()
        await self._session.refresh(audit_log)
        return audit_log

    async def list(
        self,
        tenant_id: uuid.UUID,
        accion: str | None = None,
        actor_id: uuid.UUID | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.deleted_at.is_(None),
            )
            .order_by(AuditLog.fecha_hora.desc())
            .limit(limit)
            .offset(offset)
        )
        if accion is not None:
            stmt = stmt.where(AuditLog.accion == accion)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
