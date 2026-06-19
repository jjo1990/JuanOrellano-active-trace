from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import UserInfo
from app.schemas.perfil import PerfilResponse, PerfilUpdate
from app.services.perfil_service import PerfilService

router = APIRouter(prefix="/api/perfil", tags=["perfil"])


@router.get("", response_model=PerfilResponse)
async def get_perfil(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = PerfilService(db, user.tenant_id)
    return await svc.get_perfil(user.id)


@router.patch("", response_model=PerfilResponse)
async def update_perfil(
    body: PerfilUpdate,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = PerfilService(db, user.tenant_id)
    return await svc.update_perfil(user.id, body)
