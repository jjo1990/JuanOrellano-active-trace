"""Router de encuentros — slots, instancias, admin, aula virtual."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.action_codes import ENCUENTROS_GESTIONAR
from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.encuentro import (
    AdminEncuentrosFilterParams,
    AulaVirtualResponse,
    InstanciaCreateRequest,
    InstanciaResponse,
    InstanciaUpdateRequest,
    SlotCreateRequest,
    SlotResponse,
)
from app.services.encuentro_service import EncuentroService

router = APIRouter(prefix="/api/encuentros", tags=["encuentros"])


@router.post("/slots", response_model=SlotResponse, status_code=201)
async def crear_slot(
    body: SlotCreateRequest,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    slot = await svc.crear_slot(body, user.tenant_id, user.id)
    await db.commit()
    instancias = await svc._inst_repo.list_by_slot(slot.id, user.tenant_id)
    return SlotResponse(
        id=slot.id,
        titulo=slot.titulo,
        hora=slot.hora,
        dia_semana=slot.dia_semana,
        fecha_inicio=slot.fecha_inicio,
        cant_semanas=slot.cant_semanas,
        fecha_unica=slot.fecha_unica,
        meet_url=slot.meet_url,
        materia_id=slot.materia_id,
        asignacion_id=slot.asignacion_id,
        created_at=slot.created_at,
        instancias=[InstanciaResponse.model_validate(i) for i in instancias],
    )


@router.get("/slots/{slot_id}", response_model=SlotResponse)
async def get_slot(
    slot_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    slot = await svc.get_slot_con_instancias(slot_id, user.tenant_id)
    instancias = await svc._inst_repo.list_by_slot(slot.id, user.tenant_id)
    return SlotResponse(
        id=slot.id,
        titulo=slot.titulo,
        hora=slot.hora,
        dia_semana=slot.dia_semana,
        fecha_inicio=slot.fecha_inicio,
        cant_semanas=slot.cant_semanas,
        fecha_unica=slot.fecha_unica,
        meet_url=slot.meet_url,
        materia_id=slot.materia_id,
        asignacion_id=slot.asignacion_id,
        created_at=slot.created_at,
        instancias=[InstanciaResponse.model_validate(i) for i in instancias],
    )


@router.get("/slots/{slot_id}/instancias", response_model=list[InstanciaResponse])
async def list_instancias(
    slot_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    slot = await svc.get_slot_con_instancias(slot_id, user.tenant_id)
    instancias = await svc._inst_repo.list_by_slot(slot.id, user.tenant_id)
    return [InstanciaResponse.model_validate(i) for i in instancias]


@router.get("/slots/{slot_id}/aula-virtual", response_model=AulaVirtualResponse)
async def aula_virtual(
    slot_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    html = await svc.generar_html_aula_virtual(slot_id, user.tenant_id)
    return AulaVirtualResponse(html=html)


@router.post("/instancias", response_model=InstanciaResponse, status_code=201)
async def crear_instancia(
    body: InstanciaCreateRequest,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    inst = await svc.crear_instancia(body, user.tenant_id, user.id)
    await db.commit()
    return InstanciaResponse.model_validate(inst)


@router.put("/instancias/{instancia_id}", response_model=InstanciaResponse)
async def editar_instancia(
    instancia_id: uuid.UUID,
    body: InstanciaUpdateRequest,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    inst = await svc.editar_instancia(instancia_id, body, user.tenant_id, user.id)
    await db.commit()
    return InstanciaResponse.model_validate(inst)


@router.delete("/instancias/{instancia_id}", status_code=204)
async def borrar_instancia(
    instancia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    await svc._inst_repo.soft_delete(instancia_id)
    await db.commit()
    return Response(status_code=204)


@router.get("/mis-encuentros", response_model=list[SlotResponse])
async def mis_encuentros(
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = EncuentroService(db, user.tenant_id)
    return await svc.list_mis_encuentros(user.tenant_id, user.id)


@router.get("/admin", response_model=list[SlotResponse])
async def admin_encuentros(
    materia_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    user: UserInfo = Depends(require_permission(ENCUENTROS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    from datetime import date as _date
    filtros = AdminEncuentrosFilterParams(
        materia_id=materia_id,
        estado=estado,
        fecha_desde=_date.fromisoformat(fecha_desde) if fecha_desde else None,
        fecha_hasta=_date.fromisoformat(fecha_hasta) if fecha_hasta else None,
    )
    svc = EncuentroService(db, user.tenant_id)
    return await svc.list_admin(user.tenant_id, filtros)
