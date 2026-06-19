"""Router de guardias — registro, consulta, edicion, exportacion CSV."""

import uuid
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.action_codes import GUARDIAS_REGISTRAR
from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.guardia import GuardiaCreateRequest, GuardiaResponse, GuardiaUpdateRequest
from app.services.guardia_service import GuardiaService

router = APIRouter(prefix="/api/guardias", tags=["guardias"])


@router.post("", response_model=GuardiaResponse, status_code=201)
async def registrar_guardia(
    body: GuardiaCreateRequest,
    user: UserInfo = Depends(require_permission(GUARDIAS_REGISTRAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = GuardiaService(db, user.tenant_id)
    guardia = await svc.registrar(body, user.tenant_id, user.id)
    await db.commit()
    return GuardiaResponse(
        id=guardia.id,
        materia_id=guardia.materia_id,
        carrera_id=guardia.carrera_id,
        cohorte_id=guardia.cohorte_id,
        asignacion_id=guardia.asignacion_id,
        dia=guardia.dia,
        horario=guardia.horario,
        estado=guardia.estado,
        comentarios=guardia.comentarios,
        creada_at=guardia.created_at,
    )


@router.get("", response_model=list[GuardiaResponse])
async def listar_guardias(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    user: UserInfo = Depends(require_permission(GUARDIAS_REGISTRAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = GuardiaService(db, user.tenant_id)
    return await svc.listar(
        user.tenant_id, user.id,
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        estado=estado,
    )


@router.get("/{guardia_id}", response_model=GuardiaResponse)
async def get_guardia(
    guardia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(GUARDIAS_REGISTRAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = GuardiaService(db, user.tenant_id)
    guardia = await svc._repo.get(guardia_id)
    if guardia is None:
        raise HTTPException(status_code=404, detail="Guardia no encontrada.")
    return GuardiaResponse(
        id=guardia.id,
        materia_id=guardia.materia_id,
        carrera_id=guardia.carrera_id,
        cohorte_id=guardia.cohorte_id,
        asignacion_id=guardia.asignacion_id,
        dia=guardia.dia,
        horario=guardia.horario,
        estado=guardia.estado,
        comentarios=guardia.comentarios,
        creada_at=guardia.created_at,
    )


@router.put("/{guardia_id}", response_model=GuardiaResponse)
async def editar_guardia(
    guardia_id: uuid.UUID,
    body: GuardiaUpdateRequest,
    user: UserInfo = Depends(require_permission(GUARDIAS_REGISTRAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = GuardiaService(db, user.tenant_id)
    guardia = await svc.editar(guardia_id, body, user.tenant_id, user.id)
    await db.commit()
    return GuardiaResponse(
        id=guardia.id,
        materia_id=guardia.materia_id,
        carrera_id=guardia.carrera_id,
        cohorte_id=guardia.cohorte_id,
        asignacion_id=guardia.asignacion_id,
        dia=guardia.dia,
        horario=guardia.horario,
        estado=guardia.estado,
        comentarios=guardia.comentarios,
        creada_at=guardia.created_at,
    )


@router.delete("/{guardia_id}", status_code=204)
async def borrar_guardia(
    guardia_id: uuid.UUID,
    user: UserInfo = Depends(require_permission(GUARDIAS_REGISTRAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = GuardiaService(db, user.tenant_id)
    await svc._repo.soft_delete(guardia_id)
    await db.commit()
    return Response(status_code=204)


@router.get("/exportar")
async def exportar_guardias(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    user: UserInfo = Depends(require_permission(GUARDIAS_REGISTRAR)),
    db: AsyncSession = Depends(get_db),
):
    svc = GuardiaService(db, user.tenant_id)
    csv_content = await svc.exportar_csv(
        user.tenant_id, user.id,
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        estado=estado,
    )
    return StreamingResponse(
        StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="guardias.csv"',
        },
    )
