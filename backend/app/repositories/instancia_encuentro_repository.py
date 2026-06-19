import uuid
from datetime import date
from typing import Sequence

from sqlalchemy import select

from app.models.instancia_encuentro import InstanciaEncuentro
from app.repositories.base import Repository


class InstanciaEncuentroRepository(Repository[InstanciaEncuentro]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, InstanciaEncuentro)

    async def list_by_slot(self, slot_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[InstanciaEncuentro]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.slot_id == slot_id,
                InstanciaEncuentro.tenant_id == tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
            )
            .order_by(InstanciaEncuentro.fecha)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_materia(
        self, materia_id: uuid.UUID, tenant_id: uuid.UUID,
        estado: str | None = None,
    ) -> Sequence[InstanciaEncuentro]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.materia_id == materia_id,
                InstanciaEncuentro.tenant_id == tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
            )
            .order_by(InstanciaEncuentro.fecha)
        )
        if estado is not None:
            stmt = stmt.where(InstanciaEncuentro.estado == estado)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_fecha_range(
        self, tenant_id: uuid.UUID, desde: date, hasta: date,
    ) -> Sequence[InstanciaEncuentro]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.tenant_id == tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
                InstanciaEncuentro.fecha >= desde,
                InstanciaEncuentro.fecha <= hasta,
            )
            .order_by(InstanciaEncuentro.fecha)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_independientes(
        self, tenant_id: uuid.UUID, materia_id: uuid.UUID,
    ) -> Sequence[InstanciaEncuentro]:
        stmt = (
            select(InstanciaEncuentro)
            .where(
                InstanciaEncuentro.slot_id.is_(None),
                InstanciaEncuentro.materia_id == materia_id,
                InstanciaEncuentro.tenant_id == tenant_id,
                InstanciaEncuentro.deleted_at.is_(None),
            )
            .order_by(InstanciaEncuentro.fecha)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
