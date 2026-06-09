import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
from tests.conftest import StubEntity


@pytest.mark.needs_db
class TestUserRepository:
    async def test_create_user_with_unique_email(self, db_session: AsyncSession, tenant_a):
        repo = UserRepository(session=db_session, tenant_id=tenant_a.id)
        user = User(email="alice@test.com", password_hash="hash1", display_name="Alice")
        created = await repo.create(user)
        assert created.id is not None
        assert created.email == "alice@test.com"
        assert created.tenant_id == tenant_a.id

    async def test_duplicate_email_in_same_tenant_fails(self, db_session: AsyncSession, tenant_a):
        repo = UserRepository(session=db_session, tenant_id=tenant_a.id)
        user1 = User(email="alice@test.com", password_hash="hash1", display_name="Alice")
        await repo.create(user1)
        user2 = User(email="alice@test.com", password_hash="hash2", display_name="Alice Dup")
        with pytest.raises(sa.exc.IntegrityError):
            await repo.create(user2)

    async def test_same_email_in_different_tenant_is_valid(self, db_session: AsyncSession, tenant_a, tenant_b):
        repo_a = UserRepository(session=db_session, tenant_id=tenant_a.id)
        repo_b = UserRepository(session=db_session, tenant_id=tenant_b.id)
        user_a = User(email="alice@test.com", password_hash="hash1", display_name="Alice")
        await repo_a.create(user_a)
        user_b = User(email="alice@test.com", password_hash="hash2", display_name="Alice B")
        created_b = await repo_b.create(user_b)
        assert created_b.email == "alice@test.com"
        assert created_b.tenant_id == tenant_b.id

    async def test_get_by_email_and_tenant(self, db_session: AsyncSession, tenant_a):
        repo = UserRepository(session=db_session, tenant_id=tenant_a.id)
        user = User(email="bob@test.com", password_hash="hash1", display_name="Bob")
        await repo.create(user)
        found = await repo.get_by_email("bob@test.com", tenant_a.id)
        assert found is not None
        assert found.email == "bob@test.com"

    async def test_get_by_email_wrong_tenant_returns_none(self, db_session: AsyncSession, tenant_a, tenant_b):
        repo = UserRepository(session=db_session, tenant_id=tenant_a.id)
        user = User(email="bob@test.com", password_hash="hash1", display_name="Bob")
        await repo.create(user)
        found = await repo.get_by_email("bob@test.com", tenant_b.id)
        assert found is None

    async def test_soft_delete_user(self, db_session: AsyncSession, tenant_a):
        repo = UserRepository(session=db_session, tenant_id=tenant_a.id)
        user = User(email="carol@test.com", password_hash="hash1", display_name="Carol")
        created = await repo.create(user)
        await repo.soft_delete(created.id)
        found = await repo.get(created.id)
        assert found is None
