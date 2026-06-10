import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.schemas.auth import UserInfo
from app.schemas.estructura import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate,
    CohorteCreate,
    CohorteResponse,
    CohorteUpdate,
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate,
)
from app.services.estructura import EstructuraService

router = APIRouter(prefix="/api/admin", tags=["estructura"])

# ── Carrera ───────────────────────────────────────────────────────────────


@router.get("/carreras", response_model=list[CarreraResponse])
async def list_carreras(
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.list_carreras()


@router.post("/carreras", response_model=CarreraResponse, status_code=201)
async def create_carrera(
    body: CarreraCreate,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.create_carrera(body)


@router.put("/carreras/{carrera_id}", response_model=CarreraResponse)
async def update_carrera(
    carrera_id: uuid.UUID,
    body: CarreraUpdate,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.update_carrera(carrera_id, body)


@router.delete("/carreras/{carrera_id}")
async def delete_carrera(
    carrera_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    await svc.delete_carrera(carrera_id)
    return {"message": "Carrera eliminada correctamente."}


# ── Cohorte ───────────────────────────────────────────────────────────────


@router.get("/cohortes", response_model=list[CohorteResponse])
async def list_cohortes(
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.list_cohortes()


@router.post("/cohortes", response_model=CohorteResponse, status_code=201)
async def create_cohorte(
    body: CohorteCreate,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.create_cohorte(body)


@router.put("/cohortes/{cohorte_id}", response_model=CohorteResponse)
async def update_cohorte(
    cohorte_id: uuid.UUID,
    body: CohorteUpdate,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.update_cohorte(cohorte_id, body)


@router.delete("/cohortes/{cohorte_id}")
async def delete_cohorte(
    cohorte_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    await svc.delete_cohorte(cohorte_id)
    return {"message": "Cohorte eliminada correctamente."}


# ── Materia ───────────────────────────────────────────────────────────────


@router.get("/materias", response_model=list[MateriaResponse])
async def list_materias(
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.list_materias()


@router.post("/materias", response_model=MateriaResponse, status_code=201)
async def create_materia(
    body: MateriaCreate,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.create_materia(body)


@router.put("/materias/{materia_id}", response_model=MateriaResponse)
async def update_materia(
    materia_id: uuid.UUID,
    body: MateriaUpdate,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    return await svc.update_materia(materia_id, body)


@router.delete("/materias/{materia_id}")
async def delete_materia(
    materia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EstructuraService(db, user.tenant_id)
    await svc.delete_materia(materia_id)
    return {"message": "Materia eliminada correctamente."}
