import hashlib
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.needs_db
class TestRefreshTokenRepository:
    async def _create_user(self, db_session: AsyncSession, tenant_id) -> User:
        repo = UserRepository(session=db_session, tenant_id=tenant_id)
        user = User(email="test@test.com", password_hash="hash", display_name="Test")
        return await repo.create(user)

    def _hash_token(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    async def test_create_refresh_token(self, db_session: AsyncSession, tenant_a):
        user = await self._create_user(db_session, tenant_a.id)
        repo = RefreshTokenRepository(session=db_session, tenant_id=tenant_a.id)
        token_hash = self._hash_token("raw-token-value")
        rt = RefreshToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        created = await repo.create(rt)
        assert created.id is not None
        assert created.token_hash == token_hash

    async def test_get_by_hash(self, db_session: AsyncSession, tenant_a):
        user = await self._create_user(db_session, tenant_a.id)
        repo = RefreshTokenRepository(session=db_session, tenant_id=tenant_a.id)
        token_hash = self._hash_token("find-me")
        rt = RefreshToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        await repo.create(rt)
        found = await repo.get_by_hash(token_hash)
        assert found is not None
        assert found.token_hash == token_hash

    async def test_get_by_hash_not_found(self, db_session: AsyncSession, tenant_a):
        repo = RefreshTokenRepository(session=db_session, tenant_id=tenant_a.id)
        found = await repo.get_by_hash("nonexistent-hash")
        assert found is None

    async def test_revoke_token(self, db_session: AsyncSession, tenant_a):
        user = await self._create_user(db_session, tenant_a.id)
        repo = RefreshTokenRepository(session=db_session, tenant_id=tenant_a.id)
        token_hash = self._hash_token("revoke-me")
        rt = RefreshToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        created = await repo.create(rt)
        await repo.revoke(created)
        assert created.revoked_at is not None

    async def test_revoke_all_for_user(self, db_session: AsyncSession, tenant_a):
        user = await self._create_user(db_session, tenant_a.id)
        repo = RefreshTokenRepository(session=db_session, tenant_id=tenant_a.id)
        for i in range(3):
            rt = RefreshToken(
                token_hash=self._hash_token(f"token-{i}"),
                user_id=user.id,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
            await repo.create(rt)
        await repo.revoke_all_for_user(user.id)
        for i in range(3):
            found = await repo.get_by_hash(self._hash_token(f"token-{i}"))
            assert found is None or found.revoked_at is not None
