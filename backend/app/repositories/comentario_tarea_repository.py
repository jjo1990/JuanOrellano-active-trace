import uuid
from typing import Sequence

from sqlalchemy import select

from app.models.comentario_tarea import ComentarioTarea
from app.repositories.base import Repository


class ComentarioTareaRepository(Repository[ComentarioTarea]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, ComentarioTarea)

    async def list_by_tarea(
        self, tenant_id: uuid.UUID, tarea_id: uuid.UUID,
    ) -> Sequence[ComentarioTarea]:
        stmt = (
            select(ComentarioTarea)
            .where(
                ComentarioTarea.tenant_id == tenant_id,
                ComentarioTarea.tarea_id == tarea_id,
                ComentarioTarea.deleted_at.is_(None),
            )
            .order_by(ComentarioTarea.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
