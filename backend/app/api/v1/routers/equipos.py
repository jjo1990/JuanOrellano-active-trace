import uuid
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.equipo import (
    AsignacionMasivaRequest,
    AsignacionMasivaResponse,
    BuscarUsuariosParams,
    ClonarEquipoRequest,
    ClonarEquipoResponse,
    ExportarEquipoParams,
    MisEquiposFilterParams,
    MisEquiposResponse,
    ModificarVigenciaRequest,
    ModificarVigenciaResponse,
    UsuarioAutocompletadoResponse,
)
from app.services.equipo_service import EquipoService

router = APIRouter(prefix="/api", tags=["equipos"])


@router.get("/equipos/mis-equipos", response_model=list[MisEquiposResponse])
async def mis_equipos(
    filters: MisEquiposFilterParams = Depends(),
    user: UserInfo = Depends(require_permission("equipos:ver_propio")),
    db: AsyncSession = Depends(get_db),
):
    svc = EquipoService(db, user.tenant_id)
    return await svc.get_mis_equipos(user.id, filters)


@router.post(
    "/equipos/asignacion-masiva",
    response_model=AsignacionMasivaResponse,
    status_code=201,
)
async def asignacion_masiva(
    body: AsignacionMasivaRequest,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EquipoService(db, user.tenant_id)
    result = await svc.asignacion_masiva(body)
    await db.commit()
    return result


@router.post(
    "/equipos/clonar",
    response_model=ClonarEquipoResponse,
    status_code=201,
)
async def clonar_equipo(
    body: ClonarEquipoRequest,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EquipoService(db, user.tenant_id)
    return await svc.clonar_equipo(body)


@router.put(
    "/equipos/vigencia",
    response_model=ModificarVigenciaResponse,
)
async def modificar_vigencia(
    body: ModificarVigenciaRequest,
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EquipoService(db, user.tenant_id)
    return await svc.modificar_vigencia_bloque(body)


@router.get("/equipos/exportar")
async def exportar_equipo(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    vigente: bool | None = Query(None),
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    if not materia_id and not carrera_id and not cohorte_id:
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un filtro: materia_id, carrera_id o cohorte_id.",
        )
    filters = ExportarEquipoParams(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        vigente=vigente,
    )
    svc = EquipoService(db, user.tenant_id)
    csv_content = await svc.exportar_equipo(filters)
    return StreamingResponse(
        StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="equipo_docente.csv"',
        },
    )


@router.get(
    "/equipos/buscar-usuarios",
    response_model=list[UsuarioAutocompletadoResponse],
)
async def buscar_usuarios(
    params: BuscarUsuariosParams = Depends(),
    user: UserInfo = Depends(require_permission("equipos:asignar")),
    db: AsyncSession = Depends(get_db),
):
    svc = EquipoService(db, user.tenant_id)
    return await svc.buscar_usuarios(params)
