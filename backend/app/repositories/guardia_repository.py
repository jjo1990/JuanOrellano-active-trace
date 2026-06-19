import uuid
from typing import Sequence

from sqlalchemy import select

from app.models.guardia import Guardia
from app.repositories.base import Repository


class GuardiaRepository(Repository[Guardia]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Guardia)

    async def list_by_materia(self, materia_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[Guardia]:
        return await self.list(materia_id=materia_id)

    async def list_by_asignacion(self, asignacion_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[Guardia]:
        return await self.list(asignacion_id=asignacion_id)

    async def list_with_filters(
        self,
        tenant_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
        asignacion_id: uuid.UUID | None = None,
    ) -> Sequence[Guardia]:
        stmt = (
            select(Guardia)
            .where(
                Guardia.tenant_id == tenant_id,
                Guardia.deleted_at.is_(None),
            )
            .order_by(Guardia.created_at)
        )
        if materia_id is not None:
            stmt = stmt.where(Guardia.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Guardia.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Guardia.cohorte_id == cohorte_id)
        if estado is not None:
            stmt = stmt.where(Guardia.estado == estado)
        if asignacion_id is not None:
            stmt = stmt.where(Guardia.asignacion_id == asignacion_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()
