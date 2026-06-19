import uuid
from typing import Sequence

from sqlalchemy import select

from app.models.slot_encuentro import SlotEncuentro
from app.repositories.base import Repository


class SlotEncuentroRepository(Repository[SlotEncuentro]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, SlotEncuentro)

    async def get_by_id(self, entity_id: uuid.UUID, tenant_id: uuid.UUID) -> SlotEncuentro | None:
        return await self.get(entity_id)

    async def list_by_materia(self, materia_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[SlotEncuentro]:
        return await self.list(materia_id=materia_id)

    async def list_by_asignacion(self, asignacion_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[SlotEncuentro]:
        return await self.list(asignacion_id=asignacion_id)
