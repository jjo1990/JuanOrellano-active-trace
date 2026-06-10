import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.schemas.auth import UserInfo
from app.schemas.rbac import PermisoResponse, RolCreate, RolPermisoAssign, RolResponse

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("", response_model=list[RolResponse])
async def list_roles(
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Rol).where(
        Rol.tenant_id == user.tenant_id,
        Rol.deleted_at.is_(None),
    ).order_by(Rol.nombre)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return [
        RolResponse(
            id=r.id,
            nombre=r.nombre,
            descripcion=r.descripcion,
            tenant_id=r.tenant_id,
            created_at=r.created_at,
            deleted_at=r.deleted_at,
        )
        for r in roles
    ]


@router.post("", response_model=RolResponse, status_code=201)
async def create_rol(
    body: RolCreate,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Rol).where(
        Rol.nombre == body.nombre,
        Rol.tenant_id == user.tenant_id,
        Rol.deleted_at.is_(None),
    )
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ya existe un rol con ese nombre en este tenant.")

    rol = Rol(nombre=body.nombre, descripcion=body.descripcion)
    rol.tenant_id = user.tenant_id
    db.add(rol)
    await db.commit()
    await db.refresh(rol)

    return RolResponse(
        id=rol.id,
        nombre=rol.nombre,
        descripcion=rol.descripcion,
        tenant_id=rol.tenant_id,
        created_at=rol.created_at,
        deleted_at=rol.deleted_at,
    )


@router.delete("/{rol_id}")
async def delete_rol(
    rol_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Rol).where(
        Rol.id == rol_id,
        Rol.tenant_id == user.tenant_id,
        Rol.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    rol = result.scalar_one_or_none()
    if rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")

    rol.deleted_at = func.now()
    await db.commit()
    return {"message": "Rol eliminado correctamente."}


@router.post("/{rol_id}/permisos")
async def assign_permiso_to_rol(
    rol_id: uuid.UUID,
    body: RolPermisoAssign,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Rol).where(
        Rol.id == rol_id,
        Rol.tenant_id == user.tenant_id,
        Rol.deleted_at.is_(None),
    )
    rol = (await db.execute(stmt)).scalar_one_or_none()
    if rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")

    permiso = await db.get(Permiso, body.permiso_id)
    if permiso is None or permiso.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Permiso no encontrado.")

    stmt = select(RolPermiso).where(
        RolPermiso.rol_id == rol_id,
        RolPermiso.permiso_id == body.permiso_id,
        RolPermiso.tenant_id == user.tenant_id,
        RolPermiso.deleted_at.is_(None),
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="El permiso ya está asignado a este rol.")

    rp = RolPermiso(rol_id=rol_id, permiso_id=body.permiso_id)
    rp.tenant_id = user.tenant_id
    db.add(rp)
    await db.commit()
    return {"message": "Permiso asignado correctamente."}


@router.delete("/{rol_id}/permisos/{permiso_id}")
async def remove_permiso_from_rol(
    rol_id: uuid.UUID,
    permiso_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("usuarios:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RolPermiso).where(
        RolPermiso.rol_id == rol_id,
        RolPermiso.permiso_id == permiso_id,
        RolPermiso.tenant_id == user.tenant_id,
        RolPermiso.deleted_at.is_(None),
    )
    rp = (await db.execute(stmt)).scalar_one_or_none()
    if rp is None:
        raise HTTPException(status_code=404, detail="Asignación no encontrada.")

    rp.deleted_at = func.now()
    await db.commit()
    return {"message": "Permiso removido correctamente."}
