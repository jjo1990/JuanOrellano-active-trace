from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_from_header, require_permission
from app.repositories.audit_log import AuditLogRepository
from app.schemas.auth import UserInfo


class AuditLogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    fecha_hora: datetime
    actor_id: UUID
    impersonado_id: UUID | None = None
    materia_id: UUID | None = None
    accion: str
    detalle: dict | None = None
    filas_afectadas: int = 0
    ip: str | None = None
    user_agent: str | None = None


class AuditLogListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AuditLogEntry]
    limit: int
    offset: int


router = APIRouter(prefix="/api/audit-log", tags=["audit-log"])


@router.get("")
async def list_audit_log(
    accion: str | None = Query(None),
    actor_id: UUID | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: UserInfo = Depends(require_permission("auditoria:ver")),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
):
    repo = AuditLogRepository(db)
    items = await repo.list(
        tenant_id=tenant_id,
        accion=accion,
        actor_id=actor_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )
    return AuditLogListResponse(
        items=[AuditLogEntry.model_validate(r) for r in items],
        limit=limit,
        offset=offset,
    )
