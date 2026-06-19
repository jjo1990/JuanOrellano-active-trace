import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso
from app.repositories.base import Repository


class AvisoRepository(Repository[Aviso]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Aviso)

    async def list_activos_en_ventana(self, tenant_id: uuid.UUID) -> Sequence[Aviso]:
        ahora = datetime.now(timezone.utc)
        stmt = (
            select(Aviso)
            .where(
                Aviso.tenant_id == tenant_id,
                Aviso.deleted_at.is_(None),
                Aviso.activo.is_(True),
                Aviso.inicio_en <= ahora,
                Aviso.fin_en >= ahora,
            )
            .order_by(Aviso.orden.asc(), Aviso.inicio_en.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_alcance(self, tenant_id: uuid.UUID, alcance: str) -> Sequence[Aviso]:
        stmt = (
            select(Aviso)
            .where(
                Aviso.tenant_id == tenant_id,
                Aviso.deleted_at.is_(None),
                Aviso.alcance == alcance,
            )
            .order_by(Aviso.orden.asc(), Aviso.inicio_en.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
