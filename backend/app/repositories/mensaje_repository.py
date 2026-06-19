import uuid
from typing import Sequence

from sqlalchemy import func, select

from app.models.mensaje import Mensaje
from app.repositories.base import Repository


class MensajeRepository(Repository[Mensaje]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, Mensaje)

    async def list_threads_for_user(self, user_id: uuid.UUID) -> Sequence[Mensaje]:
        stmt = (
            select(Mensaje)
            .where(
                Mensaje.tenant_id == self._tenant_id,
                Mensaje.destinatario_id == user_id,
                Mensaje.mensaje_padre_id.is_(None),
                Mensaje.deleted_at.is_(None),
            )
            .order_by(Mensaje.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_respuestas(self, mensaje_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(
            Mensaje.tenant_id == self._tenant_id,
            Mensaje.mensaje_padre_id == mensaje_id,
            Mensaje.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_ultima_respuesta_at(self, mensaje_id: uuid.UUID):
        stmt = (
            select(Mensaje.created_at)
            .where(
                Mensaje.tenant_id == self._tenant_id,
                Mensaje.mensaje_padre_id == mensaje_id,
                Mensaje.deleted_at.is_(None),
            )
            .order_by(Mensaje.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row

    async def get_thread(
        self, mensaje_id: uuid.UUID,
    ) -> tuple[Mensaje | None, Sequence[Mensaje]]:
        root = await self.get(mensaje_id)
        if root is None:
            return None, []

        stmt = (
            select(Mensaje)
            .where(
                Mensaje.tenant_id == self._tenant_id,
                Mensaje.mensaje_padre_id == mensaje_id,
                Mensaje.deleted_at.is_(None),
            )
            .order_by(Mensaje.created_at.asc())
        )
        result = await self._session.execute(stmt)
        replies = result.scalars().all()
        return root, replies

    async def user_can_access_thread(
        self, user_id: uuid.UUID, mensaje_id: uuid.UUID,
    ) -> bool:
        root = await self.get(mensaje_id)
        if root is None:
            return False

        if root.destinatario_id == user_id or root.remitente_id == user_id:
            return True

        stmt = select(func.count()).where(
            Mensaje.tenant_id == self._tenant_id,
            Mensaje.mensaje_padre_id == mensaje_id,
            Mensaje.remitente_id == user_id,
            Mensaje.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()
        return count > 0
