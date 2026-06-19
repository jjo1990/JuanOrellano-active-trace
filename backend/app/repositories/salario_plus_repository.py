import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, or_, select

from app.models.salario_plus import SalarioPlus
from app.repositories.base import Repository


class SalarioPlusRepository(Repository[SalarioPlus]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, SalarioPlus)

    async def list_by_grupo(self, grupo: str) -> Sequence[SalarioPlus]:
        return await self.list(grupo=grupo)

    async def get_vigente(self, grupo: str, rol: str, fecha: date) -> SalarioPlus | None:
        stmt = (
            select(SalarioPlus)
            .where(
                SalarioPlus.tenant_id == self._tenant_id,
                SalarioPlus.deleted_at.is_(None),
                SalarioPlus.grupo == grupo,
                SalarioPlus.rol == rol,
                SalarioPlus.desde <= fecha,
                or_(SalarioPlus.hasta.is_(None), SalarioPlus.hasta >= fecha),
            )
            .order_by(SalarioPlus.monto.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def existe_solapamiento(
        self, grupo: str, rol: str, desde: date, hasta: date | None,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        conditions = [
            SalarioPlus.tenant_id == self._tenant_id,
            SalarioPlus.deleted_at.is_(None),
            SalarioPlus.grupo == grupo,
            SalarioPlus.rol == rol,
        ]
        if hasta is not None:
            conditions.append(
                and_(
                    SalarioPlus.desde <= hasta,
                    or_(SalarioPlus.hasta.is_(None), SalarioPlus.hasta >= desde),
                )
            )
        else:
            conditions.append(
                or_(
                    SalarioPlus.hasta.is_(None),
                    SalarioPlus.hasta >= desde,
                )
            )
        if exclude_id is not None:
            conditions.append(SalarioPlus.id != exclude_id)

        stmt = select(SalarioPlus).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
