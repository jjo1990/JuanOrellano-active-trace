import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.fecha_academica import (
    CalendarioResponse,
    CronogramaResponse,
    FechaCreateRequest,
    FechaResponse,
    FechaUpdateRequest,
)
from app.services.fecha_academica_service import FechaAcademicaService

router = APIRouter(prefix="/api/fechas-academicas", tags=["fechas-academicas"])


@router.post("", response_model=FechaResponse, status_code=201)
async def create_fecha(
    body: FechaCreateRequest,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FechaAcademicaService(db, user.tenant_id)
    return await svc.create(body)


@router.get("", response_model=list[FechaResponse])
async def list_fechas(
    materia_id: uuid.UUID | None = Query(default=None),
    cohorte_id: uuid.UUID | None = Query(default=None),
    tipo: str | None = Query(default=None),
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    filters = {}
    if materia_id is not None:
        filters["materia_id"] = materia_id
    if cohorte_id is not None:
        filters["cohorte_id"] = cohorte_id
    if tipo is not None:
        filters["tipo"] = tipo
    svc = FechaAcademicaService(db, user.tenant_id)
    return await svc.list_with_filters(**filters)


@router.get("/calendario", response_model=CalendarioResponse)
async def get_calendario(
    cohorte_id: uuid.UUID = Query(...),
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FechaAcademicaService(db, user.tenant_id)
    calendario = await svc.get_calendario(cohorte_id)
    return CalendarioResponse(calendario=calendario)


@router.get("/cronograma-lms", response_model=CronogramaResponse)
async def get_cronograma_lms(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FechaAcademicaService(db, user.tenant_id)
    html = await svc.generate_cronograma_html(materia_id, cohorte_id)
    return CronogramaResponse(html=html)


@router.put("/{id}", response_model=FechaResponse)
async def update_fecha(
    id: uuid.UUID,
    body: FechaUpdateRequest,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FechaAcademicaService(db, user.tenant_id)
    return await svc.update(id, body)


@router.delete("/{id}")
async def delete_fecha(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FechaAcademicaService(db, user.tenant_id)
    await svc.delete(id)
    return {"message": "Fecha academica eliminada correctamente."}
