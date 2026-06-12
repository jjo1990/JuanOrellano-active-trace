import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.analisis import (
    AdminMonitorResponse,
    AtrasadosResponse,
    MonitorResponse,
    NotasFinalesResponse,
    RankingResponse,
    ReportesResponse,
    SeguimientoResponse,
    SinCorregirResponse,
)
from app.schemas.auth import UserInfo
from app.services.analisis_service import AnalisisService
from app.services.monitor_service import MonitorService

router = APIRouter(prefix="/api/analisis", tags=["analisis"])


def _build_service(user: UserInfo, db: AsyncSession) -> AnalisisService:
    return AnalisisService(db, user.tenant_id)


def _build_monitor_service(user: UserInfo, db: AsyncSession) -> MonitorService:
    return MonitorService(db, user.tenant_id)


@router.get("/atrasados/{materia_id}", response_model=AtrasadosResponse)
async def get_atrasados(
    materia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_atrasados(materia_id)


@router.get("/ranking/{materia_id}", response_model=RankingResponse)
async def get_ranking(
    materia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_ranking(materia_id)


@router.get("/reportes/{materia_id}", response_model=ReportesResponse)
async def get_reportes(
    materia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_reportes(materia_id)


@router.get("/notas-finales/{materia_id}", response_model=NotasFinalesResponse)
async def get_notas_finales(
    materia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_notas_finales(materia_id)


@router.get("/sin-corregir/{materia_id}", response_model=SinCorregirResponse)
async def get_sin_corregir(
    materia_id: uuid.UUID,
    reporte_token: str = Query(..., description="Token del reporte de finalizacion"),
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_sin_corregir(materia_id, reporte_token)


@router.get("/monitor", response_model=MonitorResponse)
async def get_monitor(
    materia_id: uuid.UUID | None = Query(None),
    regional: str | None = Query(None),
    comision: str | None = Query(None),
    alumno: str | None = Query(None),
    estado: str | None = Query(None),
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_monitor_service(user, db)
    return await svc.get_monitor(
        materia_id=materia_id,
        regional=regional,
        comision=comision,
        alumno=alumno,
        estado=estado,
    )


@router.get("/monitor/seguimiento", response_model=SeguimientoResponse)
async def get_monitor_seguimiento(
    alumno: str | None = Query(None),
    comision: str | None = Query(None),
    regional: str | None = Query(None),
    actividad: str | None = Query(None),
    min_aprobadas: int | None = Query(None),
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_monitor_service(user, db)
    return await svc.get_monitor_seguimiento(
        user_id=user.id,
        alumno=alumno,
        comision=comision,
        regional=regional,
        actividad=actividad,
        min_aprobadas=min_aprobadas,
    )


@router.get("/monitor/admin", response_model=AdminMonitorResponse)
async def get_monitor_admin(
    materia_id: uuid.UUID | None = Query(None),
    regional: str | None = Query(None),
    comision: str | None = Query(None),
    alumno: str | None = Query(None),
    estado: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    user: UserInfo = Depends(require_permission("atrasados:ver")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_monitor_service(user, db)
    return await svc.get_monitor_admin(
        materia_id=materia_id,
        regional=regional,
        comision=comision,
        alumno=alumno,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
