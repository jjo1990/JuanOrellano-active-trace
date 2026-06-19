"""Router de tareas internas — CRUD, delegacion, comentarios (C-16)."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.action_codes import TAREAS_GESTIONAR
from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.tarea import (
    ComentarioCreateRequest,
    ComentarioResponse,
    TareaCreateRequest,
    TareaDelegarRequest,
    TareaEstadoRequest,
    TareaResponse,
    TareaUpdateRequest,
)
from app.services.tarea_service import TareaService

router = APIRouter(prefix="/api/tareas", tags=["tareas"])


@router.post("", response_model=TareaResponse, status_code=201)
async def create_tarea(
    body: TareaCreateRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.crear_tarea(body, user.tenant_id, user.id)


@router.get("/mis-tareas", response_model=list[TareaResponse])
async def list_mis_tareas(
    materia_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.list_mis_tareas(
        user.tenant_id, user.id, materia_id=materia_id, estado=estado,
    )


@router.get("/admin", response_model=list[TareaResponse])
async def list_admin(
    asignado_a: uuid.UUID | None = Query(None),
    asignado_por: uuid.UUID | None = Query(None),
    materia_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    q: str | None = Query(None),
    user: UserInfo = Depends(require_permission(TAREAS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.list_admin(
        user.tenant_id,
        asignado_a=asignado_a,
        asignado_por=asignado_por,
        materia_id=materia_id,
        estado=estado,
        q=q,
    )


@router.get("/{id}", response_model=TareaResponse)
async def get_tarea(
    id: uuid.UUID,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.get_tarea(id, user.tenant_id)


@router.put("/{id}", response_model=TareaResponse)
async def update_tarea(
    id: uuid.UUID,
    body: TareaUpdateRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.editar_tarea(id, body, user.tenant_id)


@router.put("/{id}/estado", response_model=TareaResponse)
async def change_estado(
    id: uuid.UUID,
    body: TareaEstadoRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.cambiar_estado(id, body, user.tenant_id, user.id)


@router.put("/{id}/delegar", response_model=TareaResponse)
async def delegar_tarea(
    id: uuid.UUID,
    body: TareaDelegarRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.delegar_tarea(id, body, user.tenant_id, user.id)


@router.post("/{id}/comentarios", response_model=ComentarioResponse, status_code=201)
async def add_comentario(
    id: uuid.UUID,
    body: ComentarioCreateRequest,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.agregar_comentario(id, body, user.tenant_id, user.id)


@router.get("/{id}/comentarios", response_model=list[ComentarioResponse])
async def list_comentarios(
    id: uuid.UUID,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = TareaService(db, user.tenant_id)
    return await svc.list_comentarios(user.tenant_id, id)
