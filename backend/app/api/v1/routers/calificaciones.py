import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.calificaciones import (
    ConfirmCalificacionesRequest,
    ConfirmCalificacionesResponse,
    ImportCalificacionesPreviewResponse,
    ImportFinalizacionResponse,
    UmbralMateriaDTO,
    UmbralMateriaUpdate,
)
from app.services.calificaciones_service import CalificacionesService

router = APIRouter(prefix="/api/calificaciones", tags=["calificaciones"])


@router.post("/import", response_model=ImportCalificacionesPreviewResponse)
async def import_calificaciones(
    file: UploadFile = File(...),
    materia_id: str = Form(...),
    cohorte_id: str = Form(...),
    asignacion_id: str = Form(...),
    user: UserInfo = Depends(require_permission("calificaciones:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = CalificacionesService(db, user.tenant_id)
    return await svc.import_preview(
        file,
        uuid.UUID(materia_id),
        uuid.UUID(cohorte_id),
        uuid.UUID(asignacion_id),
        user.id,
    )


@router.post("/confirm/{preview_token}", response_model=ConfirmCalificacionesResponse)
async def confirm_import(
    preview_token: str,
    body: ConfirmCalificacionesRequest,
    user: UserInfo = Depends(require_permission("calificaciones:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = CalificacionesService(db, user.tenant_id)
    return await svc.confirm_import(preview_token, body.actividades_seleccionadas)


@router.post("/import-finalizacion", response_model=ImportFinalizacionResponse)
async def import_finalizacion(
    file: UploadFile = File(...),
    materia_id: str = Form(...),
    cohorte_id: str = Form(...),
    asignacion_id: str = Form(...),
    user: UserInfo = Depends(require_permission("calificaciones:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = CalificacionesService(db, user.tenant_id)
    return await svc.import_finalizacion(
        file,
        uuid.UUID(materia_id),
        uuid.UUID(cohorte_id),
        uuid.UUID(asignacion_id),
        user.id,
    )


@router.get("/umbral/{materia_id}", response_model=UmbralMateriaDTO)
async def get_umbral(
    materia_id: uuid.UUID,
    asignacion_id: str,
    user: UserInfo = Depends(require_permission("calificaciones:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = CalificacionesService(db, user.tenant_id)
    return await svc.get_umbral(materia_id, uuid.UUID(asignacion_id))


@router.put("/umbral/{materia_id}", response_model=UmbralMateriaDTO)
async def update_umbral(
    materia_id: uuid.UUID,
    asignacion_id: str,
    body: UmbralMateriaUpdate,
    user: UserInfo = Depends(require_permission("calificaciones:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = CalificacionesService(db, user.tenant_id)
    return await svc.upsert_umbral(materia_id, uuid.UUID(asignacion_id), body)
