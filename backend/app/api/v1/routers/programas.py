import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.programa import (
    ProgramaCreateRequest,
    ProgramaResponse,
    ProgramaUpdateRequest,
)
from app.services.programa_service import ProgramaService

router = APIRouter(prefix="/api/programas", tags=["programas"])


@router.post("", response_model=ProgramaResponse, status_code=201)
async def create_programa(
    body: ProgramaCreateRequest,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProgramaService(db, user.tenant_id)
    return await svc.create(body)


@router.get("", response_model=list[ProgramaResponse])
async def list_programas(
    materia_id: uuid.UUID | None = Query(default=None),
    carrera_id: uuid.UUID | None = Query(default=None),
    cohorte_id: uuid.UUID | None = Query(default=None),
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    filters = {}
    if materia_id is not None:
        filters["materia_id"] = materia_id
    if carrera_id is not None:
        filters["carrera_id"] = carrera_id
    if cohorte_id is not None:
        filters["cohorte_id"] = cohorte_id
    svc = ProgramaService(db, user.tenant_id)
    return await svc.list_all(**filters)


@router.get("/{id}", response_model=ProgramaResponse)
async def get_programa(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProgramaService(db, user.tenant_id)
    result = await svc.get(id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Programa no encontrado.")
    return result


@router.put("/{id}", response_model=ProgramaResponse)
async def update_programa(
    id: uuid.UUID,
    body: ProgramaUpdateRequest,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProgramaService(db, user.tenant_id)
    return await svc.update(id, body)


@router.delete("/{id}")
async def delete_programa(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProgramaService(db, user.tenant_id)
    await svc.delete(id)
    return {"message": "Programa eliminado correctamente."}
