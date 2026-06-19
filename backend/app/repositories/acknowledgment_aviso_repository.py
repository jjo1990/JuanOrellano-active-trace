import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.repositories.base import Repository


class AcknowledgmentAvisoRepository(Repository[AcknowledgmentAviso]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, AcknowledgmentAviso)

    async def get_by_aviso_usuario(
        self, aviso_id: uuid.UUID, usuario_id: uuid.UUID
    ) -> AcknowledgmentAviso | None:
        stmt = select(AcknowledgmentAviso).where(
            AcknowledgmentAviso.aviso_id == aviso_id,
            AcknowledgmentAviso.usuario_id == usuario_id,
            AcknowledgmentAviso.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_aviso(self, aviso_id: uuid.UUID) -> int:
        stmt = (
            select(func.count(AcknowledgmentAviso.id))
            .where(
                AcknowledgmentAviso.aviso_id == aviso_id,
                AcknowledgmentAviso.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
