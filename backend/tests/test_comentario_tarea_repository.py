"""Tests para ComentarioTareaRepository (C-16)."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comentario_tarea import ComentarioTarea
from app.models.tarea import Tarea
from app.models.user import User
from app.repositories.comentario_tarea_repository import ComentarioTareaRepository


@pytest.fixture
async def seed_comentario_repo(tenant_a, db_session: AsyncSession):
    tenant_id = tenant_a.id

    user = User(
        email="autor_com@test.com", password_hash="hash",
        nombre="Autor", apellidos="Comentario", tenant_id=tenant_id,
    )
    db_session.add(user)
    await db_session.flush()

    tarea = Tarea(
        tenant_id=tenant_id,
        asignado_a=user.id,
        asignado_por=user.id,
        estado="Pendiente",
        descripcion="Tarea con comentarios",
    )
    db_session.add(tarea)
    await db_session.flush()

    c1 = ComentarioTarea(
        tenant_id=tenant_id,
        tarea_id=tarea.id,
        autor_id=user.id,
        texto="Primer comentario",
    )
    c2 = ComentarioTarea(
        tenant_id=tenant_id,
        tarea_id=tarea.id,
        autor_id=user.id,
        texto="Segundo comentario",
    )
    db_session.add_all([c1, c2])
    await db_session.commit()
    for c in [c1, c2]:
        await db_session.refresh(c)

    return {
        "tenant_id": tenant_id,
        "tarea_id": tarea.id,
        "autor_id": user.id,
        "c1_id": c1.id,
        "c2_id": c2.id,
    }


@pytest.mark.needs_db
class TestComentarioTareaRepository:
    async def test_create_comentario(self, seed_comentario_repo, db_session):
        repo = ComentarioTareaRepository(db_session, seed_comentario_repo["tenant_id"])
        comentario = ComentarioTarea(
            tarea_id=seed_comentario_repo["tarea_id"],
            autor_id=seed_comentario_repo["autor_id"],
            texto="Nuevo comentario",
        )
        created = await repo.create(comentario)
        assert created.id is not None
        assert created.tenant_id == seed_comentario_repo["tenant_id"]
        assert created.texto == "Nuevo comentario"

    async def test_list_by_tarea_ordered(self, seed_comentario_repo, db_session):
        repo = ComentarioTareaRepository(db_session, seed_comentario_repo["tenant_id"])
        results = await repo.list_by_tarea(
            seed_comentario_repo["tenant_id"],
            seed_comentario_repo["tarea_id"],
        )
        assert len(results) == 2
        assert results[0].texto == "Primer comentario"
        assert results[1].texto == "Segundo comentario"

    async def test_list_by_tarea_empty(self, tenant_a, db_session):
        repo = ComentarioTareaRepository(db_session, tenant_a.id)
        results = await repo.list_by_tarea(tenant_a.id, uuid.uuid4())
        assert len(results) == 0

    async def test_tenant_isolation(self, seed_comentario_repo, tenant_b, db_session):
        repo_b = ComentarioTareaRepository(db_session, tenant_b.id)
        results = await repo_b.list_by_tarea(
            tenant_b.id, seed_comentario_repo["tarea_id"],
        )
        assert len(results) == 0
