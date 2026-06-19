import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, or_, select

from app.models.salario_base import SalarioBase
from app.repositories.base import Repository


class SalarioBaseRepository(Repository[SalarioBase]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, SalarioBase)

    async def list_by_rol(self, rol: str) -> Sequence[SalarioBase]:
        return await self.list(rol=rol)

    async def get_vigente(self, rol: str, fecha: date) -> SalarioBase | None:
        stmt = (
            select(SalarioBase)
            .where(
                SalarioBase.tenant_id == self._tenant_id,
                SalarioBase.deleted_at.is_(None),
                SalarioBase.rol == rol,
                SalarioBase.desde <= fecha,
                or_(SalarioBase.hasta.is_(None), SalarioBase.hasta >= fecha),
            )
            .order_by(SalarioBase.monto.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def existe_solapamiento(
        self, rol: str, desde: date, hasta: date | None, exclude_id: uuid.UUID | None = None,
    ) -> bool:
        conditions = [
            SalarioBase.tenant_id == self._tenant_id,
            SalarioBase.deleted_at.is_(None),
            SalarioBase.rol == rol,
        ]
        if hasta is not None:
            conditions.append(
                and_(
                    SalarioBase.desde <= hasta,
                    or_(SalarioBase.hasta.is_(None), SalarioBase.hasta >= desde),
                )
            )
        else:
            conditions.append(
                or_(
                    SalarioBase.hasta.is_(None),
                    SalarioBase.hasta >= desde,
                )
            )
        if exclude_id is not None:
            conditions.append(SalarioBase.id != exclude_id)

        stmt = select(SalarioBase).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
