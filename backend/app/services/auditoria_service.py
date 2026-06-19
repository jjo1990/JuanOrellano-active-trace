import uuid
from collections.abc import Sequence
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.repositories.audit_log import AuditLogRepository
from app.schemas.auditoria import (
    AccionesPorDia,
    EstadoComunicacion,
    InteraccionDocenteMateria,
    LogEntryResponse,
    LogFilterParams,
    LogListResponse,
    PanelFilterParams,
    PanelResponse,
    UltimaAccion,
)


class AuditoriaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._repo = AuditLogRepository(session)

    async def _get_scope_materia_ids(self, user_id: uuid.UUID) -> list[uuid.UUID] | None:
        hoy = date.today()
        stmt = (
            select(Asignacion.materia_id)
            .where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.usuario_id == user_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.desde <= hoy,
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= hoy),
                Asignacion.materia_id.isnot(None),
            )
            .distinct()
        )
        result = await self._session.execute(stmt)
        ids = [row[0] for row in result.fetchall()]
        return ids if ids else None

    @staticmethod
    def _to_dt(fecha: date | None, end_of_day: bool = False) -> datetime | None:
        if fecha is None:
            return None
        if end_of_day:
            return datetime.combine(fecha, datetime.max.time(), tzinfo=timezone.utc)
        return datetime.combine(fecha, datetime.min.time(), tzinfo=timezone.utc)

    async def get_panel(
        self,
        filters: PanelFilterParams,
        user_id: uuid.UUID,
    ) -> PanelResponse:
        scope_materia_ids = await self._get_scope_materia_ids(user_id)
        materia_ids = self._resolve_materia_ids(filters.materia_id, scope_materia_ids)

        fecha_desde = self._to_dt(filters.fecha_desde)
        fecha_hasta = self._to_dt(filters.fecha_hasta, end_of_day=True)

        actor_id = filters.usuario_id

        acciones_raw = await self._repo.count_by_date(
            tenant_id=self._tenant_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_ids=materia_ids,
        )
        acciones_por_dia = [
            AccionesPorDia(**item) for item in acciones_raw
        ]

        estado_raw = await self._repo.count_by_estado_comunicacion(
            tenant_id=self._tenant_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_ids=materia_ids,
        )
        estado_comunicaciones = [
            EstadoComunicacion(**item) for item in estado_raw
        ]

        inter_raw = await self._repo.count_by_docente_accion(
            tenant_id=self._tenant_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_ids=materia_ids,
        )
        interacciones = [
            InteraccionDocenteMateria(**item) for item in inter_raw
        ]

        logs = await self._repo.list_with_filters(
            tenant_id=self._tenant_id,
            actor_id=actor_id,
            materia_ids=materia_ids,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=filters.limite,
            offset=0,
        )
        ultimas = [UltimaAccion.model_validate(r) for r in logs]

        return PanelResponse(
            acciones_por_dia=acciones_por_dia,
            estado_comunicaciones=estado_comunicaciones,
            interacciones_docente_materia=interacciones,
            ultimas_acciones=ultimas,
        )

    async def get_log(
        self,
        filters: LogFilterParams,
        user_id: uuid.UUID,
    ) -> LogListResponse:
        scope_materia_ids = await self._get_scope_materia_ids(user_id)
        materia_ids = self._resolve_materia_ids(filters.materia_id, scope_materia_ids)

        fecha_desde = self._to_dt(filters.fecha_desde)
        fecha_hasta = self._to_dt(filters.fecha_hasta, end_of_day=True)

        actor_id = filters.usuario_id

        logs = await self._repo.list_with_filters(
            tenant_id=self._tenant_id,
            accion=filters.accion,
            actor_id=actor_id,
            materia_ids=materia_ids,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=filters.limite,
            offset=filters.offset,
        )

        total = await self._repo.count_with_filters(
            tenant_id=self._tenant_id,
            accion=filters.accion,
            actor_id=actor_id,
            materia_ids=materia_ids,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

        items = [LogEntryResponse.model_validate(r) for r in logs]

        return LogListResponse(
            items=items,
            limite=filters.limite,
            offset=filters.offset,
            total=total,
        )

    @staticmethod
    def _resolve_materia_ids(
        request_materia_id: uuid.UUID | None,
        scope_materia_ids: list[uuid.UUID] | None,
    ) -> list[uuid.UUID] | None:
        if request_materia_id is not None:
            if scope_materia_ids is not None and request_materia_id not in scope_materia_ids:
                return []
            return [request_materia_id]
        return scope_materia_ids
