import uuid
from typing import Sequence

from sqlalchemy import select

from app.models.tarea import Tarea
from app.repositories.base import Repository


class TareaRepository(Repository[Tarea]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Tarea)

    async def list_by_asignado(
        self,
        tenant_id: uuid.UUID,
        asignado_a: uuid.UUID,
        estado: str | None = None,
        materia_id: uuid.UUID | None = None,
    ) -> Sequence[Tarea]:
        stmt = (
            select(Tarea)
            .where(
                Tarea.tenant_id == tenant_id,
                Tarea.asignado_a == asignado_a,
                Tarea.deleted_at.is_(None),
            )
            .order_by(Tarea.created_at.desc())
        )
        if estado is not None:
            stmt = stmt.where(Tarea.estado == estado)
        if materia_id is not None:
            stmt = stmt.where(Tarea.materia_id == materia_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_with_filters(
        self,
        tenant_id: uuid.UUID,
        asignado_a: uuid.UUID | None = None,
        asignado_por: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
        q: str | None = None,
    ) -> Sequence[Tarea]:
        stmt = (
            select(Tarea)
            .where(
                Tarea.tenant_id == tenant_id,
                Tarea.deleted_at.is_(None),
            )
            .order_by(Tarea.created_at.desc())
        )
        if asignado_a is not None:
            stmt = stmt.where(Tarea.asignado_a == asignado_a)
        if asignado_por is not None:
            stmt = stmt.where(Tarea.asignado_por == asignado_por)
        if materia_id is not None:
            stmt = stmt.where(Tarea.materia_id == materia_id)
        if estado is not None:
            stmt = stmt.where(Tarea.estado == estado)
        if q is not None:
            stmt = stmt.where(Tarea.descripcion.ilike(f"%{q}%"))
        result = await self._session.execute(stmt)
        return result.scalars().all()
