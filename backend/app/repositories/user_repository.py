import uuid
from typing import Sequence

from sqlalchemy import or_, select

from app.models.user import User
from app.repositories.base import Repository


class UserRepository(Repository[User]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(
            User.email == email,
            User.tenant_id == self._tenant_id,
            User.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(self) -> Sequence[User]:
        return await self.list()

    async def search_by_name(self, query: str) -> Sequence[User]:
        pattern = f"%{query}%"
        stmt = (
            select(User)
            .where(
                User.tenant_id == self._tenant_id,
                User.deleted_at.is_(None),
                or_(
                    User.nombre.ilike(pattern),
                    User.apellidos.ilike(pattern),
                ),
            )
            .order_by(User.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def filter_by_active(self, activo: bool) -> Sequence[User]:
        return await self.list(activo=activo)
