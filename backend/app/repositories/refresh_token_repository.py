import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update as sa_update

from app.models.refresh_token import RefreshToken
from app.repositories.base import Repository


class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, RefreshToken)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await self._session.merge(token)
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            sa_update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.deleted_at.is_(None),
            )
            .values(revoked_at=func.now())
        )
        await self._session.execute(stmt)
        await self._session.flush()
