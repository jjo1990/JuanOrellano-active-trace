from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.permiso import Permiso
from app.schemas.auth import UserInfo
from app.schemas.rbac import PermisoResponse

router = APIRouter(prefix="/api/v1/permisos", tags=["permisos"])


@router.get("", response_model=list[PermisoResponse])
async def list_permisos(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Permiso).where(
        Permiso.deleted_at.is_(None),
    ).order_by(Permiso.codigo)
    result = await db.execute(stmt)
    permisos = result.scalars().all()
    return [
        PermisoResponse(
            id=p.id,
            codigo=p.codigo,
            descripcion=p.descripcion,
            modulo=p.modulo,
        )
        for p in permisos
    ]
