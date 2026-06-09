"""Tests para Repository[T] genérico con scope de tenant (RED → GREEN → TRIANGULATE)."""

import uuid

import pytest

from app.core.exceptions import RepositoryError
from app.repositories.base import Repository
from tests.conftest import StubEntity


@pytest.mark.needs_db
class TestRepositoryGet:
    async def test_get_returns_entity_for_own_tenant(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo.create(StubEntity(name="propio"))
        found = await repo.get(entity.id)
        assert found is not None
        assert found.id == entity.id
        assert found.name == "propio"

    async def test_get_returns_none_for_other_tenant(self, db_session, tenant_a, tenant_b):
        repo_a = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo_a.create(StubEntity(name="solo-A"))
        repo_b = Repository[StubEntity](db_session, tenant_b.id, StubEntity)
        found = await repo_b.get(entity.id)
        assert found is None

    async def test_get_returns_none_for_nonexistent_id(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        found = await repo.get(uuid.uuid4())
        assert found is None


@pytest.mark.needs_db
class TestRepositoryList:
    async def test_list_only_returns_entities_of_current_tenant(
        self, db_session, tenant_a, tenant_b,
    ):
        repo_a = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        repo_b = Repository[StubEntity](db_session, tenant_b.id, StubEntity)

        await repo_a.create(StubEntity(name="A-1"))
        await repo_a.create(StubEntity(name="A-2"))
        await repo_b.create(StubEntity(name="B-1"))

        items_a = await repo_a.list()
        assert len(items_a) == 2
        assert all(e.name.startswith("A-") for e in items_a)

    async def test_list_returns_empty_when_no_entities(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        items = await repo.list()
        assert items == []

    async def test_list_with_filters(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        await repo.create(StubEntity(name="alpha"))
        await repo.create(StubEntity(name="beta"))

        items = await repo.list(name="alpha")
        assert len(items) == 1
        assert items[0].name == "alpha"

    async def test_list_excludes_soft_deleted(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        e1 = await repo.create(StubEntity(name="visible"))
        e2 = await repo.create(StubEntity(name="oculto"))
        await repo.soft_delete(e2.id)

        items = await repo.list()
        names = [e.name for e in items]
        assert "visible" in names
        assert "oculto" not in names


@pytest.mark.needs_db
class TestRepositoryCreate:
    async def test_create_assigns_tenant_id(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = StubEntity(name="test")
        created = await repo.create(entity)
        assert created.tenant_id == tenant_a.id
        assert created.id is not None

    async def test_create_multiple_entities(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        e1 = await repo.create(StubEntity(name="uno"))
        e2 = await repo.create(StubEntity(name="dos"))
        assert e1.id != e2.id
        items = await repo.list()
        assert len(items) == 2


@pytest.mark.needs_db
class TestRepositoryUpdate:
    async def test_update_modifies_entity(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo.create(StubEntity(name="original"))
        entity.name = "modificado"
        updated = await repo.update(entity)
        assert updated.name == "modificado"

    async def test_update_rejects_entity_from_other_tenant(
        self, db_session, tenant_a, tenant_b,
    ):
        repo_a = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo_a.create(StubEntity(name="de-A"))

        repo_b = Repository[StubEntity](db_session, tenant_b.id, StubEntity)
        # NO modificamos tenant_id — el entity original tiene tenant_a.id
        # repo_b debe rechazar porque entity.tenant_id != repo_b._tenant_id
        entity.name = "hackeado"
        with pytest.raises(RepositoryError):
            await repo_b.update(entity)


@pytest.mark.needs_db
class TestRepositorySoftDelete:
    async def test_soft_delete_marks_deleted_at(self, db_session, tenant_a):
        repo = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo.create(StubEntity(name="to-delete"))
        await repo.soft_delete(entity.id)

        found = await repo.get(entity.id)
        assert found is None

    async def test_soft_delete_rejects_entity_from_other_tenant(
        self, db_session, tenant_a, tenant_b,
    ):
        repo_a = Repository[StubEntity](db_session, tenant_a.id, StubEntity)
        entity = await repo_a.create(StubEntity(name="de-A"))

        repo_b = Repository[StubEntity](db_session, tenant_b.id, StubEntity)
        with pytest.raises(RepositoryError):
            await repo_b.soft_delete(entity.id)

        found_in_a = await repo_a.get(entity.id)
        assert found_in_a is not None
