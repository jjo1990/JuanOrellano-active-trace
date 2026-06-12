import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.schemas.auth import UserInfo
from app.schemas.padron import (
    ConfirmResponse,
    EntradaPadronDTO,
    ImportPreviewResponse,
    VaciarResponse,
    VersionPadronDTO,
)
from app.services.padron_service import PadronService

router = APIRouter(prefix="/api/padron", tags=["padron"])


@router.post("/import", response_model=ImportPreviewResponse)
async def import_padron_preview(
    file: UploadFile = File(...),
    materia_id: str = Form(...),
    cohorte_id: str = Form(...),
    user: UserInfo = Depends(require_permission("padron:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = PadronService(db, user.tenant_id)
    return await svc.import_preview(
        file, uuid.UUID(materia_id), uuid.UUID(cohorte_id), user.id,
    )


@router.post("/confirm/{preview_token}", response_model=ConfirmResponse)
async def confirm_import_padron(
    preview_token: str,
    user: UserInfo = Depends(require_permission("padron:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = PadronService(db, user.tenant_id)
    return await svc.confirm_import(preview_token)


@router.delete("/vaciar/{materia_id}", response_model=VaciarResponse)
async def vaciar_materia_padron(
    materia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("padron:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = PadronService(db, user.tenant_id)
    return await svc.vaciar_materia(materia_id, user.id)


@router.get("/versions", response_model=list[VersionPadronDTO])
async def list_versions(
    materia_id: str | None = None,
    user: UserInfo = Depends(require_permission("padron:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = PadronService(db, user.tenant_id)
    return await svc.list_versions(
        materia_id=uuid.UUID(materia_id) if materia_id else None,
    )


@router.get("/entradas/{version_id}", response_model=list[EntradaPadronDTO])
async def list_entradas(
    version_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("padron:importar")),
    db: AsyncSession = Depends(get_db),
):
    svc = PadronService(db, user.tenant_id)
    return await svc.get_entradas(version_id)
