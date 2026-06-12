import uuid
from collections.abc import Sequence

from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comunicacion import Comunicacion
from app.repositories.base import Repository


class ComunicacionRepository(Repository[Comunicacion]):
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Comunicacion)

    async def get_pendientes(self, limit: int = 10) -> Sequence[Comunicacion]:
        stmt = (
            select(Comunicacion)
            .where(
                Comunicacion.tenant_id == self._tenant_id,
                Comunicacion.deleted_at.is_(None),
                Comunicacion.estado == "Pendiente",
                (Comunicacion.lote_id.is_(None)) | (Comunicacion.lote_aprobado.is_(True)),
            )
            .order_by(Comunicacion.created_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_lote(self, lote_id: uuid.UUID) -> Sequence[Comunicacion]:
        stmt = (
            select(Comunicacion)
            .where(
                Comunicacion.tenant_id == self._tenant_id,
                Comunicacion.deleted_at.is_(None),
                Comunicacion.lote_id == lote_id,
            )
            .order_by(Comunicacion.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_materia(
        self, materia_id: uuid.UUID, estado: str | None = None,
    ) -> Sequence[Comunicacion]:
        stmt = (
            select(Comunicacion)
            .where(
                Comunicacion.tenant_id == self._tenant_id,
                Comunicacion.deleted_at.is_(None),
                Comunicacion.materia_id == materia_id,
            )
            .order_by(Comunicacion.created_at)
        )
        if estado is not None:
            stmt = stmt.where(Comunicacion.estado == estado)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def aprobar_lote(self, lote_id: uuid.UUID) -> int:
        stmt = (
            sa_update(Comunicacion)
            .where(
                Comunicacion.lote_id == lote_id,
                Comunicacion.tenant_id == self._tenant_id,
                Comunicacion.deleted_at.is_(None),
                Comunicacion.estado == "Pendiente",
                Comunicacion.lote_aprobado.is_(False),
            )
            .values(lote_aprobado=True)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def cancelar_lote(self, lote_id: uuid.UUID) -> int:
        stmt = (
            sa_update(Comunicacion)
            .where(
                Comunicacion.lote_id == lote_id,
                Comunicacion.tenant_id == self._tenant_id,
                Comunicacion.deleted_at.is_(None),
                Comunicacion.estado == "Pendiente",
            )
            .values(estado="Cancelado")
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
