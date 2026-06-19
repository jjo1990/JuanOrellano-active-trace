"""Router de coloquios — evaluaciones, reservas, resultados y métricas."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.action_codes import COLOQUIOS_GESTIONAR, COLOQUIOS_RESERVAR
from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.coloquio import (
    AgendaFilterParams,
    EvaluacionCreateRequest,
    EvaluacionDetailResponse,
    EvaluacionResponse,
    EvaluacionUpdateRequest,
    ImportAlumnosRequest,
    MetricasResponse,
    ReservaAgendaResponse,
    ReservaCreateRequest,
    ReservaResponse,
    ResultadoConsolidadoResponse,
    ResultadoCreateRequest,
    ResultadoResponse,
    ResultadosFilterParams,
)
from app.services.coloquio_service import ColoquioService

router = APIRouter(prefix="/api/coloquios", tags=["coloquios"])


@router.post("/evaluaciones", response_model=EvaluacionResponse, status_code=201)
async def crear_evaluacion(
    body: EvaluacionCreateRequest,
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    ev = await svc.crear_evaluacion(body, user.tenant_id)
    await db.commit()
    return EvaluacionResponse(
        id=ev.id,
        materia_id=ev.materia_id,
        cohorte_id=ev.cohorte_id,
        tipo=ev.tipo,
        instancia=ev.instancia,
        dias_disponibles=ev.dias_disponibles,
        cupos_por_dia=ev.cupos_por_dia,
        estado=ev.estado,
        created_at=ev.created_at,
    )


@router.get("/evaluaciones", response_model=list[EvaluacionResponse])
async def list_evaluaciones(
    cohorte_id: uuid.UUID | None = Query(None),
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    return await svc.list_evaluaciones(user.tenant_id, cohorte_id)


@router.get("/evaluaciones/{evaluacion_id}", response_model=EvaluacionDetailResponse)
async def get_evaluacion(
    evaluacion_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    return await svc.get_evaluacion(evaluacion_id, user.tenant_id)


@router.put("/evaluaciones/{evaluacion_id}", response_model=EvaluacionResponse)
async def editar_evaluacion(
    evaluacion_id: uuid.UUID,
    body: EvaluacionUpdateRequest,
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    ev = await svc.editar_evaluacion(evaluacion_id, body, user.tenant_id)
    await db.commit()
    return EvaluacionResponse(
        id=ev.id,
        materia_id=ev.materia_id,
        cohorte_id=ev.cohorte_id,
        tipo=ev.tipo,
        instancia=ev.instancia,
        dias_disponibles=ev.dias_disponibles,
        cupos_por_dia=ev.cupos_por_dia,
        estado=ev.estado,
        created_at=ev.created_at,
    )


@router.post("/evaluaciones/{evaluacion_id}/alumnos", status_code=200)
async def importar_alumnos(
    evaluacion_id: uuid.UUID,
    body: ImportAlumnosRequest,
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    importados = await svc.importar_alumnos(evaluacion_id, body, user.tenant_id)
    await db.commit()
    return {"importados": importados}


@router.post("/reservas", response_model=ReservaResponse, status_code=201)
async def reservar_turno(
    body: ReservaCreateRequest,
    user: UserInfo = Depends(require_permission(COLOQUIOS_RESERVAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    reserva = await svc.reservar_turno(body, user.tenant_id, user.id)
    await db.commit()
    return ReservaResponse.model_validate(reserva)


@router.delete("/reservas/{reserva_id}", status_code=204)
async def cancelar_reserva(
    reserva_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(COLOQUIOS_RESERVAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    await svc.cancelar_reserva(reserva_id, user.tenant_id, user.id, is_coordinador=False)
    await db.commit()
    return Response(status_code=204)


@router.get("/agenda", response_model=list[ReservaAgendaResponse])
async def get_agenda(
    materia_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    q: str | None = Query(None),
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime as _datetime
    filtros = AgendaFilterParams(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        fecha_desde=_datetime.fromisoformat(fecha_desde) if fecha_desde else None,
        fecha_hasta=_datetime.fromisoformat(fecha_hasta) if fecha_hasta else None,
        q=q,
    )
    svc = ColoquioService(db, user.tenant_id)
    return await svc.get_agenda(user.tenant_id, filtros)


@router.post("/resultados", response_model=ResultadoResponse, status_code=200)
async def registrar_resultado(
    body: ResultadoCreateRequest,
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    resultado = await svc.registrar_resultado(body, user.tenant_id)
    await db.commit()
    return ResultadoResponse.model_validate(resultado)


@router.get("/resultados", response_model=list[ResultadoConsolidadoResponse])
async def get_resultados(
    materia_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    pendientes: bool = Query(False),
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    filtros = ResultadosFilterParams(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        pendientes=pendientes,
    )
    svc = ColoquioService(db, user.tenant_id)
    return await svc.get_resultados(user.tenant_id, filtros)


@router.get("/metricas", response_model=MetricasResponse)
async def get_metricas(
    cohorte_id: uuid.UUID | None = Query(None),
    user: UserInfo = Depends(require_permission(COLOQUIOS_GESTIONAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = ColoquioService(db, user.tenant_id)
    return await svc.get_metricas(user.tenant_id, cohorte_id)
