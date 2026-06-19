import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select, update as sa_update

from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.repositories.base import Repository


class LiquidacionRepository(Repository[Liquidacion]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Liquidacion)

    async def list_by_cohorte_periodo(
        self, cohorte_id: uuid.UUID, periodo: str, estado: str | None = None,
    ) -> Sequence[Liquidacion]:
        stmt = (
            select(Liquidacion)
            .where(
                Liquidacion.tenant_id == self._tenant_id,
                Liquidacion.deleted_at.is_(None),
                Liquidacion.cohorte_id == cohorte_id,
                Liquidacion.periodo == periodo,
            )
            .order_by(Liquidacion.created_at)
        )
        if estado is not None:
            stmt = stmt.where(Liquidacion.estado == estado)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_usuario_cohorte_periodo(
        self, usuario_id: uuid.UUID, cohorte_id: uuid.UUID, periodo: str,
    ) -> Liquidacion | None:
        stmt = (
            select(Liquidacion)
            .where(
                Liquidacion.tenant_id == self._tenant_id,
                Liquidacion.deleted_at.is_(None),
                Liquidacion.usuario_id == usuario_id,
                Liquidacion.cohorte_id == cohorte_id,
                Liquidacion.periodo == periodo,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def cerrar_lote(self, cohorte_id: uuid.UUID, periodo: str) -> int:
        stmt = (
            sa_update(Liquidacion)
            .where(
                Liquidacion.tenant_id == self._tenant_id,
                Liquidacion.deleted_at.is_(None),
                Liquidacion.cohorte_id == cohorte_id,
                Liquidacion.periodo == periodo,
                Liquidacion.estado == EstadoLiquidacion.ABIERTA,
            )
            .values(estado=EstadoLiquidacion.CERRADA)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def list_abiertas_by_cohorte_periodo(
        self, cohorte_id: uuid.UUID, periodo: str,
    ) -> Sequence[Liquidacion]:
        return await self.list_by_cohorte_periodo(
            cohorte_id, periodo, estado=EstadoLiquidacion.ABIERTA,
        )
