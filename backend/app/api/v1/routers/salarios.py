import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.schemas.auth import UserInfo
from app.schemas.salario import (
    SalarioBaseCreate,
    SalarioBaseResponse,
    SalarioBaseUpdate,
    SalarioPlusCreate,
    SalarioPlusResponse,
    SalarioPlusUpdate,
)

router = APIRouter(prefix="/api/salarios", tags=["salarios"])


@router.post("/base", response_model=SalarioBaseResponse, status_code=201)
async def create_salario_base(
    body: SalarioBaseCreate,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioBaseRepository(db, user.tenant_id)
    if await repo.existe_solapamiento(body.rol, body.desde, body.hasta):
        raise HTTPException(
            status_code=409,
            detail="Ya existe una entrada vigente para ese rol en ese período.",
        )
    from app.models.salario_base import SalarioBase
    entity = SalarioBase(
        rol=body.rol, monto=body.monto, desde=body.desde, hasta=body.hasta,
    )
    result = await repo.create(entity)
    await db.commit()
    return result


@router.get("/base", response_model=list[SalarioBaseResponse])
async def list_salario_base(
    rol: str | None = Query(None),
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioBaseRepository(db, user.tenant_id)
    if rol:
        results = await repo.list_by_rol(rol)
    else:
        results = await repo.list()
    return results


@router.get("/base/vigente", response_model=SalarioBaseResponse)
async def get_salario_base_vigente(
    rol: str = Query(...),
    fecha: date = Query(...),
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioBaseRepository(db, user.tenant_id)
    result = await repo.get_vigente(rol, fecha)
    if result is None:
        raise HTTPException(status_code=404, detail="Sin entrada vigente.")
    return result


@router.get("/base/{id}", response_model=SalarioBaseResponse)
async def get_salario_base(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioBaseRepository(db, user.tenant_id)
    result = await repo.get(id)
    if result is None:
        raise HTTPException(status_code=404, detail="No encontrado.")
    return result


@router.put("/base/{id}", response_model=SalarioBaseResponse)
async def update_salario_base(
    id: uuid.UUID,
    body: SalarioBaseUpdate,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioBaseRepository(db, user.tenant_id)
    entity = await repo.get(id)
    if entity is None:
        raise HTTPException(status_code=404, detail="No encontrado.")

    nuevo_desde = body.desde if body.desde is not None else entity.desde
    nuevo_hasta = body.hasta if hasattr(body, 'hasta') else entity.hasta
    if await repo.existe_solapamiento(entity.rol, nuevo_desde, nuevo_hasta, exclude_id=id):
        raise HTTPException(
            status_code=409,
            detail="Ya existe una entrada vigente para ese rol en ese período.",
        )

    update_dict = body.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(entity, field, value)
    result = await repo.update(entity)
    await db.commit()
    return result


@router.delete("/base/{id}", status_code=204)
async def delete_salario_base(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioBaseRepository(db, user.tenant_id)
    await repo.soft_delete(id)
    await db.commit()


@router.post("/plus", response_model=SalarioPlusResponse, status_code=201)
async def create_salario_plus(
    body: SalarioPlusCreate,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioPlusRepository(db, user.tenant_id)
    if await repo.existe_solapamiento(body.grupo, body.rol, body.desde, body.hasta):
        raise HTTPException(
            status_code=409,
            detail="Ya existe un plus vigente para ese grupo y rol en ese período.",
        )
    from app.models.salario_plus import SalarioPlus
    entity = SalarioPlus(
        grupo=body.grupo, rol=body.rol, descripcion=body.descripcion,
        monto=body.monto, desde=body.desde, hasta=body.hasta,
    )
    result = await repo.create(entity)
    await db.commit()
    return result


@router.get("/plus", response_model=list[SalarioPlusResponse])
async def list_salario_plus(
    grupo: str | None = Query(None),
    rol: str | None = Query(None),
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioPlusRepository(db, user.tenant_id)
    if grupo:
        results = await repo.list_by_grupo(grupo)
    else:
        results = await repo.list()
    if rol:
        results = [r for r in results if r.rol == rol]
    return results


@router.get("/plus/vigente", response_model=SalarioPlusResponse)
async def get_salario_plus_vigente(
    grupo: str = Query(...),
    rol: str = Query(...),
    fecha: date = Query(...),
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioPlusRepository(db, user.tenant_id)
    result = await repo.get_vigente(grupo, rol, fecha)
    if result is None:
        raise HTTPException(status_code=404, detail="Sin entrada vigente.")
    return result


@router.get("/plus/{id}", response_model=SalarioPlusResponse)
async def get_salario_plus(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioPlusRepository(db, user.tenant_id)
    result = await repo.get(id)
    if result is None:
        raise HTTPException(status_code=404, detail="No encontrado.")
    return result


@router.put("/plus/{id}", response_model=SalarioPlusResponse)
async def update_salario_plus(
    id: uuid.UUID,
    body: SalarioPlusUpdate,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioPlusRepository(db, user.tenant_id)
    entity = await repo.get(id)
    if entity is None:
        raise HTTPException(status_code=404, detail="No encontrado.")

    nuevo_desde = body.desde if body.desde is not None else entity.desde
    nuevo_hasta = body.hasta if hasattr(body, 'hasta') else entity.hasta
    if await repo.existe_solapamiento(
        entity.grupo, entity.rol, nuevo_desde, nuevo_hasta, exclude_id=id,
    ):
        raise HTTPException(
            status_code=409,
            detail="Ya existe un plus vigente para ese grupo y rol en ese período.",
        )

    update_dict = body.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(entity, field, value)
    result = await repo.update(entity)
    await db.commit()
    return result


@router.delete("/plus/{id}", status_code=204)
async def delete_salario_plus(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("liquidaciones:configurar-salarios")),
    db: AsyncSession = Depends(get_db),
):
    repo = SalarioPlusRepository(db, user.tenant_id)
    await repo.soft_delete(id)
    await db.commit()
