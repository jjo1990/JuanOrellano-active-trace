"""Tests de aislamiento multi-tenant y soft delete."""

import pytest

from app.core.exceptions import RepositoryError
from app.repositories.base import Repository
from tests.conftest import StubEntity


@pytest.mark.needs_db
class TestMultiTenantIsolation:
    async def test_tenant_a_data_invisible_to_tenant_b(
        self, db_session, tenant_a, tenant_b,
    ):
        repo_a = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        repo_b = Repository[StubEntity](db_session, tenant_b.id, StubEntity)

        await repo_a.create(StubEntity(name="datos-A"))
        await repo_a.create(StubEntity(name="datos-A-2"))
        await repo_b.create(StubEntity(name="datos-B"))

        items_a = await repo_a.list()
        items_b = await repo_b.list()

        assert len(items_a) == 2
        assert len(items_b) == 1
        a_names = {e.name for e in items_a}
        b_names = {e.name for e in items_b}
        assert a_names.isdisjoint(b_names)

    async def test_soft_deleted_entity_not_in_list(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        e1 = await repo.create(StubEntity(name="visible"))
        e2 = await repo.create(StubEntity(name="eliminado"))

        await repo.soft_delete(e2.id)

        items = await repo.list()
        ids = {e.id for e in items}
        assert e1.id in ids
        assert e2.id not in ids

    async def test_soft_delete_plus_create_same_id_other_tenant(
        self, db_session, tenant_a, tenant_b,
    ):
        repo_a = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity_a = await repo_a.create(StubEntity(name="original-A"))

        repo_b = Repository[StubEntity](db_session, tenant_b.id, StubEntity)
        entity_b = await repo_b.create(StubEntity(name="original-B"))

        await repo_a.soft_delete(entity_a.id)

        with pytest.raises(RepositoryError):
            await repo_b.soft_delete(entity_b.id)

        deleted_check_b = await repo_b.get(entity_b.id)
        assert deleted_check_b is not None

    async def test_list_with_filters_and_soft_delete_combined(
        self, db_session, tenant_a,
    ):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        e1 = await repo.create(StubEntity(name="alfa"))
        e2 = await repo.create(StubEntity(name="beta"))
        await repo.soft_delete(e2.id)

        items = await repo.list(name="alfa")
        assert len(items) == 1
        assert items[0].id == e1.id

        items_beta = await repo.list(name="beta")
        assert len(items_beta) == 0


@pytest.mark.needs_db
class TestTimestamps:
    async def test_created_at_and_updated_at_are_set(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo.create(StubEntity(name="timestamps"))
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert entity.deleted_at is None

    async def test_updated_at_changes_on_update(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo.create(StubEntity(name="antes"))
        original_updated = entity.updated_at

        entity.name = "despues"
        updated = await repo.update(entity)
        assert updated.updated_at >= original_updated
