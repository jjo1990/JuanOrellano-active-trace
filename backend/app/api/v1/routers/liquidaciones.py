import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.liquidacion import (
    LiquidacionCalcularRequest,
    LiquidacionCalcularResponse,
    LiquidacionCerrarRequest,
    LiquidacionCerrarResponse,
    LiquidacionResponse,
    LiquidacionSegmentadaResponse,
)
from app.services.liquidacion_service import LiquidacionService

router = APIRouter(prefix="/api/liquidaciones", tags=["liquidaciones"])


@router.post("/calcular", response_model=LiquidacionCalcularResponse, status_code=201)
async def calcular(
    body: LiquidacionCalcularRequest,
    user: UserInfo = Depends(require_permission("liquidaciones:calcular")),
    db: AsyncSession = Depends(get_db),
):
    svc = LiquidacionService(db, user.tenant_id)
    return await svc.calcular(body.cohorte_id, body.periodo, user.id)


@router.get("", response_model=LiquidacionSegmentadaResponse)
async def listar_segmentado(
    cohorte_id: uuid.UUID = Query(...),
    periodo: str = Query(..., min_length=7, max_length=7),
    user: UserInfo = Depends(require_permission("liquidaciones:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = LiquidacionService(db, user.tenant_id)
    return await svc.listar_segmentado(cohorte_id, periodo)


@router.get("/{id}", response_model=LiquidacionResponse)
async def detalle(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("liquidaciones:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = LiquidacionService(db, user.tenant_id)
    return await svc.get_detalle(id)


@router.post("/{id}/recalcular", response_model=LiquidacionResponse)
async def recalcular(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("liquidaciones:calcular")),
    db: AsyncSession = Depends(get_db),
):
    svc = LiquidacionService(db, user.tenant_id)
    return await svc.recalcular(id, user.id)


@router.post("/cerrar", response_model=LiquidacionCerrarResponse)
async def cerrar(
    body: LiquidacionCerrarRequest,
    user: UserInfo = Depends(require_permission("liquidaciones:cerrar")),
    db: AsyncSession = Depends(get_db),
):
    svc = LiquidacionService(db, user.tenant_id)
    return await svc.cerrar(body.cohorte_id, body.periodo, user.id)


@router.get("/historial/list", response_model=list[LiquidacionResponse])
async def historial(
    cohorte_id: uuid.UUID | None = Query(None),
    periodo: str | None = Query(None, min_length=7, max_length=7),
    usuario_id: uuid.UUID | None = Query(None),
    user: UserInfo = Depends(require_permission("liquidaciones:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = LiquidacionService(db, user.tenant_id)
    return await svc.historial(cohorte_id, periodo, usuario_id)
