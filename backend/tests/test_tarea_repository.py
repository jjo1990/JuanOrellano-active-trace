"""Tests para TareaRepository (C-16)."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarea import Tarea
from app.models.user import User
from app.repositories.tarea_repository import TareaRepository


@pytest.fixture
async def seed_tarea_repo(tenant_a, db_session: AsyncSession):
    tenant_id = tenant_a.id

    user_1 = User(
        email="profe1_tarea@test.com", password_hash="hash",
        nombre="Profe", apellidos="Uno", tenant_id=tenant_id,
    )
    user_2 = User(
        email="profe2_tarea@test.com", password_hash="hash",
        nombre="Profe", apellidos="Dos", tenant_id=tenant_id,
    )
    db_session.add_all([user_1, user_2])
    await db_session.flush()

    t1 = Tarea(
        tenant_id=tenant_id,
        asignado_a=user_1.id,
        asignado_por=user_2.id,
        estado="Pendiente",
        descripcion="Tarea pendiente 1",
    )
    t2 = Tarea(
        tenant_id=tenant_id,
        asignado_a=user_1.id,
        asignado_por=user_2.id,
        estado="En progreso",
        descripcion="Tarea en progreso 1",
    )
    t3 = Tarea(
        tenant_id=tenant_id,
        asignado_a=user_2.id,
        asignado_por=user_1.id,
        estado="Pendiente",
        descripcion="Tarea pendiente 2",
    )
    db_session.add_all([t1, t2, t3])
    await db_session.commit()
    for t in [t1, t2, t3]:
        await db_session.refresh(t)

    return {
        "tenant_id": tenant_id,
        "user_1_id": user_1.id,
        "user_2_id": user_2.id,
        "t1_id": t1.id,
        "t2_id": t2.id,
        "t3_id": t3.id,
    }


@pytest.mark.needs_db
class TestTareaRepository:
    async def test_create_tarea(self, tenant_a, db_session):
        user = User(
            email="test_creator@test.com", password_hash="hash",
            nombre="Test", apellidos="Creator", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()

        repo = TareaRepository(db_session, tenant_a.id)
        tarea = Tarea(
            asignado_a=user.id,
            asignado_por=user.id,
            estado="Pendiente",
            descripcion="Crear reporte",
        )
        created = await repo.create(tarea)
        assert created.id is not None
        assert created.tenant_id == tenant_a.id
        assert created.estado == "Pendiente"

    async def test_list_by_asignado(self, seed_tarea_repo, db_session):
        repo = TareaRepository(db_session, seed_tarea_repo["tenant_id"])
        results = await repo.list_by_asignado(
            seed_tarea_repo["tenant_id"],
            seed_tarea_repo["user_1_id"],
        )
        assert len(results) == 2
        ids = {r.id for r in results}
        assert seed_tarea_repo["t1_id"] in ids
        assert seed_tarea_repo["t2_id"] in ids

    async def test_list_by_asignado_with_estado_filter(self, seed_tarea_repo, db_session):
        repo = TareaRepository(db_session, seed_tarea_repo["tenant_id"])
        results = await repo.list_by_asignado(
            seed_tarea_repo["tenant_id"],
            seed_tarea_repo["user_1_id"],
            estado="Pendiente",
        )
        assert len(results) == 1
        assert results[0].id == seed_tarea_repo["t1_id"]

    async def test_soft_delete_marks_deleted_at(self, seed_tarea_repo, db_session):
        repo = TareaRepository(db_session, seed_tarea_repo["tenant_id"])
        tarea_id = seed_tarea_repo["t1_id"]

        await repo.soft_delete(tarea_id)

        deleted = await repo.get(tarea_id)
        assert deleted is None

    async def test_soft_delete_nonexistent_raises(self, tenant_a, db_session):
        repo = TareaRepository(db_session, tenant_a.id)
        fake_id = uuid.uuid4()
        with pytest.raises(Exception):
            await repo.soft_delete(fake_id)

    async def test_tenant_isolation(self, seed_tarea_repo, tenant_b, db_session):
        repo_b = TareaRepository(db_session, tenant_b.id)
        results = await repo_b.list_by_asignado(
            tenant_b.id, seed_tarea_repo["user_1_id"],
        )
        assert len(results) == 0
