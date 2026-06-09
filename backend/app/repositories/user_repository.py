import uuid
from typing import Sequence

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import Repository


class UserRepository(Repository[User]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, User)

    async def get_by_email(self, email: str, tenant_id: uuid.UUID) -> User | None:
        stmt = select(User).where(
            User.email == email,
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[User]:
        return await self.list(tenant_id=tenant_id)
