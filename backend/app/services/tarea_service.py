import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comentario_tarea import ComentarioTarea
from app.models.tarea import Tarea
from app.repositories.comentario_tarea_repository import ComentarioTareaRepository
from app.repositories.tarea_repository import TareaRepository
from app.schemas.tarea import (
    ComentarioCreateRequest,
    ComentarioResponse,
    ESTADOS_VALIDOS,
    TareaCreateRequest,
    TareaDelegarRequest,
    TareaEstadoRequest,
    TareaResponse,
    TareaUpdateRequest,
)


class TareaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._tarea_repo = TareaRepository(session, tenant_id)
        self._comentario_repo = ComentarioTareaRepository(session, tenant_id)
        self._session = session
        self._tenant_id = tenant_id

    async def crear_tarea(
        self, data: TareaCreateRequest, tenant_id: uuid.UUID, asignado_por: uuid.UUID,
    ) -> TareaResponse:
        tarea = Tarea(
            tenant_id=tenant_id,
            materia_id=data.materia_id,
            asignado_a=data.asignado_a,
            asignado_por=asignado_por,
            estado="Pendiente",
            descripcion=data.descripcion,
            contexto_id=data.contexto_id,
        )
        created = await self._tarea_repo.create(tarea)
        await self._session.commit()
        await self._session.refresh(created)
        return TareaResponse.model_validate(created)

    async def list_mis_tareas(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> list[TareaResponse]:
        tareas = await self._tarea_repo.list_by_asignado(
            tenant_id, user_id, estado=estado, materia_id=materia_id,
        )
        return [TareaResponse.model_validate(t) for t in tareas]

    async def get_tarea(
        self, id: uuid.UUID, tenant_id: uuid.UUID,
    ) -> TareaResponse:
        tarea = await self._tarea_repo.get(id)
        if tarea is None:
            raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        comentarios = await self._comentario_repo.list_by_tarea(tenant_id, id)
        resp = TareaResponse.model_validate(tarea)
        resp.comentarios = [ComentarioResponse.model_validate(c) for c in comentarios]
        return resp

    async def editar_tarea(
        self, id: uuid.UUID, data: TareaUpdateRequest, tenant_id: uuid.UUID,
    ) -> TareaResponse:
        tarea = await self._tarea_repo.get(id)
        if tarea is None:
            raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(tarea, field, value)
        await self._tarea_repo.update(tarea)
        await self._session.commit()
        await self._session.refresh(tarea)
        return TareaResponse.model_validate(tarea)

    async def cambiar_estado(
        self,
        id: uuid.UUID,
        data: TareaEstadoRequest,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TareaResponse:
        if not data.estado_valido():
            raise HTTPException(
                status_code=422,
                detail=f"Estado inválido. Válidos: {', '.join(sorted(ESTADOS_VALIDOS))}",
            )
        tarea = await self._tarea_repo.get(id)
        if tarea is None:
            raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        if tarea.asignado_a != user_id:
            raise HTTPException(
                status_code=403,
                detail="Solo el asignado puede cambiar el estado de esta tarea.",
            )
        tarea.estado = data.estado
        await self._tarea_repo.update(tarea)
        await self._session.commit()
        await self._session.refresh(tarea)
        return TareaResponse.model_validate(tarea)

    async def delegar_tarea(
        self,
        id: uuid.UUID,
        data: TareaDelegarRequest,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TareaResponse:
        tarea = await self._tarea_repo.get(id)
        if tarea is None:
            raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        if tarea.asignado_a != user_id:
            raise HTTPException(
                status_code=403,
                detail="Solo el asignado actual puede delegar esta tarea.",
            )

        anterior_asignado_id = tarea.asignado_a
        tarea.asignado_a = data.nuevo_asignado_id
        await self._tarea_repo.update(tarea)

        texto_delegacion = (
            f"Tarea delegada de {anterior_asignado_id} a "
            f"{data.nuevo_asignado_id} por {user_id}"
        )
        comentario = ComentarioTarea(
            tenant_id=tenant_id,
            tarea_id=tarea.id,
            autor_id=user_id,
            texto=texto_delegacion,
        )
        await self._comentario_repo.create(comentario)

        await self._session.commit()
        await self._session.refresh(tarea)
        return TareaResponse.model_validate(tarea)

    async def list_admin(
        self,
        tenant_id: uuid.UUID,
        asignado_a: uuid.UUID | None = None,
        asignado_por: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
        q: str | None = None,
    ) -> list[TareaResponse]:
        tareas = await self._tarea_repo.list_with_filters(
            tenant_id,
            asignado_a=asignado_a,
            asignado_por=asignado_por,
            materia_id=materia_id,
            estado=estado,
            q=q,
        )
        return [TareaResponse.model_validate(t) for t in tareas]

    async def agregar_comentario(
        self,
        tarea_id: uuid.UUID,
        data: ComentarioCreateRequest,
        tenant_id: uuid.UUID,
        autor_id: uuid.UUID,
    ) -> ComentarioResponse:
        tarea = await self._tarea_repo.get(tarea_id)
        if tarea is None:
            raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        comentario = ComentarioTarea(
            tenant_id=tenant_id,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=data.texto,
        )
        created = await self._comentario_repo.create(comentario)
        await self._session.commit()
        await self._session.refresh(created)
        return ComentarioResponse.model_validate(created)

    async def list_comentarios(
        self, tenant_id: uuid.UUID, tarea_id: uuid.UUID,
    ) -> list[ComentarioResponse]:
        comentarios = await self._comentario_repo.list_by_tarea(tenant_id, tarea_id)
        return [ComentarioResponse.model_validate(c) for c in comentarios]
