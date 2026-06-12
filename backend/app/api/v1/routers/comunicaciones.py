import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.comunicacion import (
    CancelarRequest,
    ComunicacionDTO,
    EnviarRequest,
    EnviarResponse,
    LoteStatusResponse,
    PreviewRequest,
    PreviewResponse,
)
from app.services.comunicacion_service import ComunicacionService

router = APIRouter(prefix="/api/comunicaciones", tags=["comunicaciones"])


def _build_service(user: UserInfo, db: AsyncSession) -> ComunicacionService:
    return ComunicacionService(db, user.tenant_id)


@router.post("/preview", response_model=PreviewResponse)
async def preview(
    request: PreviewRequest,
    user: UserInfo = Depends(require_permission("comunicacion:enviar")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.preview(request)


@router.post("/enviar", response_model=EnviarResponse)
async def enviar(
    request: EnviarRequest,
    user: UserInfo = Depends(require_permission("comunicacion:enviar")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.enviar(request, user.id)


@router.get("/lote/{lote_id}", response_model=LoteStatusResponse)
async def get_lote_status(
    lote_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("comunicacion:enviar")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_lote_status(lote_id)


@router.get("/materia/{materia_id}", response_model=list[ComunicacionDTO])
async def get_by_materia(
    materia_id: uuid.UUID,
    estado: str | None = None,
    user: UserInfo = Depends(require_permission("comunicacion:enviar")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.get_by_materia(materia_id, estado=estado)


@router.post("/aprobar/{lote_id}", response_model=LoteStatusResponse)
async def aprobar_lote(
    lote_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("comunicacion:aprobar")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    return await svc.aprobar_lote(lote_id, user.id)


@router.post("/cancelar/{id}", response_model=ComunicacionDTO)
async def cancelar_individual(
    id: uuid.UUID,
    request: CancelarRequest | None = None,
    user: UserInfo = Depends(require_permission("comunicacion:enviar")),
    db: AsyncSession = Depends(get_db),
):
    svc = _build_service(user, db)
    motivo = request.motivo if request else None
    try:
        return await svc.cancelar_individual(id, user.id, motivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
