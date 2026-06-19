import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        self._session.add(audit_log)
        await self._session.flush()
        await self._session.refresh(audit_log)
        return audit_log

    async def list(
        self,
        tenant_id: uuid.UUID,
        accion: str | None = None,
        actor_id: uuid.UUID | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.deleted_at.is_(None),
            )
            .order_by(AuditLog.fecha_hora.desc())
            .limit(limit)
            .offset(offset)
        )
        if accion is not None:
            stmt = stmt.where(AuditLog.accion == accion)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_with_filters(
        self,
        tenant_id: uuid.UUID,
        accion: str | None = None,
        actor_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: Sequence[uuid.UUID] | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        limit: int = 200,
        offset: int = 0,
    ) -> Sequence[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.deleted_at.is_(None),
            )
            .order_by(AuditLog.fecha_hora.desc())
            .limit(limit)
            .offset(offset)
        )
        if accion is not None:
            stmt = stmt.where(AuditLog.accion == accion)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if materia_id is not None:
            stmt = stmt.where(AuditLog.materia_id == materia_id)
        if materia_ids is not None:
            if len(materia_ids) == 0:
                stmt = stmt.where(text("false"))
            else:
                stmt = stmt.where(AuditLog.materia_id.in_(materia_ids))
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_with_filters(
        self,
        tenant_id: uuid.UUID,
        accion: str | None = None,
        actor_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        materia_ids: Sequence[uuid.UUID] | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(AuditLog).where(
            AuditLog.tenant_id == tenant_id,
            AuditLog.deleted_at.is_(None),
        )
        if accion is not None:
            stmt = stmt.where(AuditLog.accion == accion)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if materia_id is not None:
            stmt = stmt.where(AuditLog.materia_id == materia_id)
        if materia_ids is not None:
            if len(materia_ids) == 0:
                stmt = stmt.where(text("false"))
            else:
                stmt = stmt.where(AuditLog.materia_id.in_(materia_ids))
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def count_by_date(
        self,
        tenant_id: uuid.UUID,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_ids: Sequence[uuid.UUID] | None = None,
    ) -> Sequence[dict]:
        fecha_col = func.date(AuditLog.fecha_hora).label("fecha")
        stmt = (
            select(fecha_col, AuditLog.accion, func.count().label("cantidad"))
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.deleted_at.is_(None),
            )
            .group_by(fecha_col, AuditLog.accion)
            .order_by(fecha_col.desc())
        )
        if materia_ids is not None:
            if len(materia_ids) == 0:
                stmt = stmt.where(text("false"))
            else:
                stmt = stmt.where(AuditLog.materia_id.in_(materia_ids))
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return [{"fecha": r[0], "accion": r[1], "cantidad": r[2]} for r in result.fetchall()]

    async def count_by_docente_accion(
        self,
        tenant_id: uuid.UUID,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_ids: Sequence[uuid.UUID] | None = None,
    ) -> Sequence[dict]:
        stmt = (
            select(
                AuditLog.actor_id.label("docente_id"),
                AuditLog.materia_id,
                AuditLog.accion,
                func.count().label("cantidad"),
            )
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.deleted_at.is_(None),
            )
            .group_by(AuditLog.actor_id, AuditLog.materia_id, AuditLog.accion)
            .order_by(func.count().desc())
        )
        if materia_ids is not None:
            if len(materia_ids) == 0:
                stmt = stmt.where(text("false"))
            else:
                stmt = stmt.where(AuditLog.materia_id.in_(materia_ids))
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return [
            {"docente_id": r[0], "materia_id": r[1], "accion": r[2], "cantidad": r[3]}
            for r in result.fetchall()
        ]

    async def count_by_estado_comunicacion(
        self,
        tenant_id: uuid.UUID,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        materia_ids: Sequence[uuid.UUID] | None = None,
    ) -> Sequence[dict]:
        detalle_accion = AuditLog.detalle["accion"].astext.label("estado")
        stmt = (
            select(
                AuditLog.actor_id.label("docente_id"),
                detalle_accion,
                func.count().label("cantidad"),
            )
            .where(
                AuditLog.tenant_id == tenant_id,
                AuditLog.deleted_at.is_(None),
                AuditLog.accion == "COMUNICACION_ENVIAR",
                AuditLog.detalle.isnot(None),
            )
            .group_by(AuditLog.actor_id, detalle_accion)
            .order_by(func.count().desc())
        )
        if materia_ids is not None:
            if len(materia_ids) == 0:
                stmt = stmt.where(text("false"))
            else:
                stmt = stmt.where(AuditLog.materia_id.in_(materia_ids))
        if fecha_desde is not None:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        result = await self._session.execute(stmt)
        return [
            {"docente_id": r[0], "estado": r[1], "cantidad": r[2]}
            for r in result.fetchall()
        ]
