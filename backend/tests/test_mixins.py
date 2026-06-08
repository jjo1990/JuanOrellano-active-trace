"""Tests para BaseModelMixin."""

import pytest

from tests.conftest import StubEntity


@pytest.mark.needs_db
class TestBaseModelMixin:
    async def test_uuid_generated_on_create(self, db_session, tenant_a):
        entity = StubEntity(name="test-uuid", tenant_id=tenant_a.id)
        db_session.add(entity)
        await db_session.flush()
        await db_session.refresh(entity)
        assert entity.id is not None

    async def test_uuid_unique_per_instance(self, db_session, tenant_a):
        e1 = StubEntity(name="uno", tenant_id=tenant_a.id)
        e2 = StubEntity(name="dos", tenant_id=tenant_a.id)
        db_session.add_all([e1, e2])
        await db_session.flush()
        assert e1.id != e2.id

    async def test_created_at_set_on_create(self, db_session, tenant_a):
        entity = StubEntity(name="test-created", tenant_id=tenant_a.id)
        db_session.add(entity)
        await db_session.flush()
        await db_session.refresh(entity)
        assert entity.created_at is not None

    async def test_tenant_id_is_nullable_for_tenant_model(self, db_session):
        from app.models.tenant import Tenant

        tenant = Tenant(nombre="Root", slug="root")
        db_session.add(tenant)
        await db_session.flush()
        await db_session.refresh(tenant)
        assert tenant.tenant_id is None

    async def test_tenant_id_is_nullable_for_non_tenant(self, db_session):
        entity = StubEntity(name="no-tenant")
        db_session.add(entity)
        await db_session.flush()
        await db_session.refresh(entity)
        assert entity.tenant_id is None
