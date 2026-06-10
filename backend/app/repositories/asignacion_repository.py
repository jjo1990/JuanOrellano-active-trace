import uuid
from datetime import date
from typing import Sequence

from sqlalchemy import select

from app.models.asignacion import Asignacion
from app.repositories.base import Repository


class AsignacionRepository(Repository[Asignacion]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Asignacion)

    async def list_by_usuario(self, usuario_id: uuid.UUID) -> Sequence[Asignacion]:
        return await self.list(usuario_id=usuario_id)

    async def list_vigentes(self, fecha: date) -> Sequence[Asignacion]:
        stmt = (
            select(Asignacion)
            .where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
                Asignacion.desde <= fecha,
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= fecha),
            )
            .order_by(Asignacion.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_by_materia(self, materia_id: uuid.UUID) -> Sequence[Asignacion]:
        return await self.list(materia_id=materia_id)

    async def list_by_rol(self, rol_id: uuid.UUID) -> Sequence[Asignacion]:
        return await self.list(rol_id=rol_id)

    async def filter_by_context(
        self,
        usuario_id: uuid.UUID | None = None,
        materia_id: uuid.UUID | None = None,
        rol_id: uuid.UUID | None = None,
        vigente: bool | None = None,
    ) -> Sequence[Asignacion]:
        stmt = (
            select(Asignacion)
            .where(
                Asignacion.tenant_id == self._tenant_id,
                Asignacion.deleted_at.is_(None),
            )
            .order_by(Asignacion.created_at)
        )
        if usuario_id is not None:
            stmt = stmt.where(Asignacion.usuario_id == usuario_id)
        if materia_id is not None:
            stmt = stmt.where(Asignacion.materia_id == materia_id)
        if rol_id is not None:
            stmt = stmt.where(Asignacion.rol_id == rol_id)
        if vigente is True:
            from datetime import date as _date_today
            hoy = _date_today.today()
            stmt = stmt.where(
                Asignacion.desde <= hoy,
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= hoy),
            )
        elif vigente is False:
            from datetime import date as _date_today
            hoy = _date_today.today()
            stmt = stmt.where(
                (Asignacion.hasta.isnot(None)) & (Asignacion.hasta < hoy),
            )
        result = await self._session.execute(stmt)
        return result.scalars().all()
