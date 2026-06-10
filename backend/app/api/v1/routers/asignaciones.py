import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionResponse,
    AsignacionUpdate,
)
from app.schemas.auth import UserInfo
from app.services.asignacion_service import AsignacionService

router = APIRouter(prefix="/api", tags=["asignaciones"])


@router.get("/asignaciones", response_model=list[AsignacionResponse])
async def list_asignaciones(
    usuario_id: uuid.UUID | None = None,
    materia_id: uuid.UUID | None = None,
    rol_id: uuid.UUID | None = None,
    vigente: bool | None = None,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AsignacionService(db, user.tenant_id)
    return await svc.list(
        usuario_id=usuario_id,
        materia_id=materia_id,
        rol_id=rol_id,
        vigente=vigente,
    )


@router.post("/asignaciones", response_model=AsignacionResponse, status_code=201)
async def create_asignacion(
    body: AsignacionCreate,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AsignacionService(db, user.tenant_id)
    return await svc.create(body)


@router.get("/asignaciones/{asignacion_id}", response_model=AsignacionResponse)
async def get_asignacion(
    asignacion_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AsignacionService(db, user.tenant_id)
    return await svc.get(asignacion_id)


@router.put("/asignaciones/{asignacion_id}", response_model=AsignacionResponse)
async def update_asignacion(
    asignacion_id: uuid.UUID,
    body: AsignacionUpdate,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AsignacionService(db, user.tenant_id)
    return await svc.update(asignacion_id, body)


@router.delete("/asignaciones/{asignacion_id}", status_code=204)
async def delete_asignacion(
    asignacion_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = AsignacionService(db, user.tenant_id)
    await svc.soft_delete(asignacion_id)
