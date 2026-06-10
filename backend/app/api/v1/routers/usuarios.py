import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioStatusUpdate,
    UsuarioUpdate,
)
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/admin", tags=["usuarios"])


@router.get("/usuarios", response_model=list[UsuarioResponse])
async def list_usuarios(
    activo: bool | None = None,
    q: str | None = None,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = UsuarioService(db, user.tenant_id)
    return await svc.list(activo=activo, q=q)


@router.post("/usuarios", response_model=UsuarioResponse, status_code=201)
async def create_usuario(
    body: UsuarioCreate,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = UsuarioService(db, user.tenant_id)
    return await svc.create(body)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = UsuarioService(db, user.tenant_id)
    return await svc.get(usuario_id)


@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: uuid.UUID,
    body: UsuarioUpdate,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = UsuarioService(db, user.tenant_id)
    return await svc.update(usuario_id, body)


@router.patch("/usuarios/{usuario_id}/status", response_model=UsuarioResponse)
async def update_usuario_status(
    usuario_id: uuid.UUID,
    body: UsuarioStatusUpdate,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = UsuarioService(db, user.tenant_id)
    return await svc.update_status(usuario_id, body)
