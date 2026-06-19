import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.aviso import (
    AvisoCreateRequest,
    AvisoResponse,
    AvisoUpdateRequest,
    AvisoVisibleResponse,
    AckResponse,
)
from app.services.aviso_service import AvisoService

router = APIRouter(prefix="/api/avisos", tags=["avisos"])


@router.post("", response_model=AvisoResponse, status_code=201)
async def create_aviso(
    body: AvisoCreateRequest,
    user: UserInfo = Depends(require_permission("avisos:publicar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    return await svc.crear_aviso(body, user.tenant_id)


@router.get("", response_model=list[AvisoResponse])
async def list_avisos(
    user: UserInfo = Depends(require_permission("avisos:publicar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    return await svc.list_avisos(user.tenant_id)


@router.get("/visibles", response_model=list[AvisoVisibleResponse])
async def list_visibles(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    return await svc.list_visibles(user.tenant_id, user.id)


@router.get("/{id}", response_model=AvisoResponse)
async def get_aviso(
    id: uuid.UUID,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    return await svc.get_aviso(id, user.tenant_id)


@router.put("/{id}", response_model=AvisoResponse)
async def update_aviso(
    id: uuid.UUID,
    body: AvisoUpdateRequest,
    user: UserInfo = Depends(require_permission("avisos:publicar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    return await svc.editar_aviso(id, body, user.tenant_id)


@router.delete("/{id}", status_code=204)
async def delete_aviso(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("avisos:publicar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    await svc.eliminar_aviso(id, user.tenant_id)


@router.post("/{id}/ack", response_model=AckResponse)
async def acknowledge_aviso(
    id: uuid.UUID,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AvisoService(db, user.tenant_id)
    await svc.acknowledge(id, user.tenant_id, user.id)
    return AckResponse(mensaje="Acuse registrado correctamente.")
