import uuid
from collections.abc import Sequence

from sqlalchemy import select

from app.models.factura import Factura
from app.repositories.base import Repository


class FacturaRepository(Repository[Factura]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Factura)

    async def list_with_filters(
        self,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
        periodo: str | None = None,
    ) -> Sequence[Factura]:
        stmt = (
            select(Factura)
            .where(
                Factura.tenant_id == self._tenant_id,
                Factura.deleted_at.is_(None),
            )
            .order_by(Factura.cargada_at.desc())
        )
        if usuario_id is not None:
            stmt = stmt.where(Factura.usuario_id == usuario_id)
        if estado is not None:
            stmt = stmt.where(Factura.estado == estado)
        if periodo is not None:
            stmt = stmt.where(Factura.periodo == periodo)
        result = await self._session.execute(stmt)
        return result.scalars().all()
