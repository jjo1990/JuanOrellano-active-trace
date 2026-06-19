import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import UserInfo
from app.schemas.mensaje import (
    MensajeCreate,
    MensajeReplyCreate,
    MensajeResponse,
    ThreadDetailResponse,
    ThreadListItem,
)
from app.services.mensaje_service import MensajeService

router = APIRouter(prefix="/api/inbox", tags=["inbox"])


@router.get("", response_model=list[ThreadListItem])
async def list_threads(
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MensajeService(db, user.tenant_id)
    return await svc.list_threads(user.id)


@router.get("/{id}", response_model=ThreadDetailResponse)
async def get_thread(
    id: uuid.UUID,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MensajeService(db, user.tenant_id)
    return await svc.get_thread(id, user.id)


@router.post("", response_model=MensajeResponse, status_code=201)
async def create_message(
    body: MensajeCreate,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MensajeService(db, user.tenant_id)
    return await svc.create_message(body, user.id)


@router.post("/{id}/reply", response_model=MensajeResponse, status_code=201)
async def reply_to_thread(
    id: uuid.UUID,
    body: MensajeReplyCreate,
    user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = MensajeService(db, user.tenant_id)
    return await svc.reply_to_thread(id, body, user.id)
