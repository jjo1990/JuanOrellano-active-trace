from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_from_header, require_permission
from app.schemas.auditoria import (
    LogFilterParams,
    LogListResponse,
    PanelFilterParams,
    PanelResponse,
)
from app.schemas.auth import UserInfo
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix="/api/auditoria", tags=["auditoria"])


@router.get("/panel")
async def get_panel(
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    materia_id: UUID | None = Query(None),
    usuario_id: UUID | None = Query(None),
    limite: int = Query(200, ge=1, le=1000),
    user: UserInfo = Depends(require_permission("auditoria:ver")),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
) -> PanelResponse:
    from datetime import date as _date

    svc = AuditoriaService(db, tenant_id)
    filtros = PanelFilterParams(
        fecha_desde=_date.fromisoformat(fecha_desde) if fecha_desde else None,
        fecha_hasta=_date.fromisoformat(fecha_hasta) if fecha_hasta else None,
        materia_id=materia_id,
        usuario_id=usuario_id,
        limite=limite,
    )
    return await svc.get_panel(filtros, user.id)


@router.get("/log")
async def get_log(
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    materia_id: UUID | None = Query(None),
    usuario_id: UUID | None = Query(None),
    accion: str | None = Query(None),
    limite: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user: UserInfo = Depends(require_permission("auditoria:ver")),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_tenant_from_header),
) -> LogListResponse:
    from datetime import date as _date

    svc = AuditoriaService(db, tenant_id)
    filtros = LogFilterParams(
        fecha_desde=_date.fromisoformat(fecha_desde) if fecha_desde else None,
        fecha_hasta=_date.fromisoformat(fecha_hasta) if fecha_hasta else None,
        materia_id=materia_id,
        usuario_id=usuario_id,
        accion=accion,
        limite=limite,
        offset=offset,
    )
    return await svc.get_log(filtros, user.id)
