import uuid
from datetime import date, datetime
from typing import Sequence

from sqlalchemy import func, select

from app.models.evaluacion import Evaluacion
from app.repositories.base import Repository


class EvaluacionRepository(Repository[Evaluacion]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Evaluacion)

    async def get_by_id(self, entity_id: uuid.UUID, tenant_id: uuid.UUID) -> Evaluacion | None:
        return await self.get(entity_id)

    async def list_by_materia(self, materia_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[Evaluacion]:
        return await self.list(materia_id=materia_id)

    async def list_by_cohorte(self, cohorte_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[Evaluacion]:
        return await self.list(cohorte_id=cohorte_id)

    async def list_all(self, tenant_id: uuid.UUID, estado: str | None = None) -> Sequence[Evaluacion]:
        if estado is not None:
            return await self.list(estado=estado)
        return await self.list()
