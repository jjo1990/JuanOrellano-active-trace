"""TDD tests for SlotEncuentroRepository."""

import uuid
from datetime import date, time

import pytest

from app.models.asignacion import Asignacion
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.slot_encuentro import SlotEncuentro
from app.models.user import User
from app.repositories.slot_encuentro_repository import SlotEncuentroRepository


@pytest.fixture
async def seed_slot_repo(db_session, tenant_a):
    user = User(
        email="slotrepo@test.com", password_hash="hash",
        nombre="Slot", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-010",
    )
    db_session.add(user)
    await db_session.flush()

    rol = Rol(nombre="PROFESOR_SLOT", descripcion="Prof Slot", tenant_id=tenant_a.id)
    db_session.add(rol)
    await db_session.flush()

    materia = Materia(codigo="MAT_SLOT", nombre="Materia Slot", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    asig = Asignacion(
        usuario_id=user.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=None, cohorte_id=None,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    db_session.add(asig)
    await db_session.flush()

    slot = SlotEncuentro(
        titulo="Clase de prueba", hora=time(18, 0),
        dia_semana="Lunes", fecha_inicio=date(2026, 3, 9),
        cant_semanas=4, materia_id=materia.id, asignacion_id=asig.id,
        tenant_id=tenant_a.id,
    )
    db_session.add(slot)
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user_id": user.id,
        "rol_id": rol.id,
        "materia_id": materia.id,
        "asig_id": asig.id,
        "slot_id": slot.id,
    }


@pytest.mark.needs_db
class TestSlotEncuentroRepository:
    async def test_get_by_id_returns_slot(self, db_session, seed_slot_repo):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_id(d["slot_id"], d["tenant_a_id"])
        assert result is not None
        assert result.titulo == "Clase de prueba"
        assert result.dia_semana == "Lunes"

    async def test_get_by_id_wrong_tenant_returns_none(self, db_session, seed_slot_repo, tenant_b):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, tenant_b.id)
        result = await repo.get_by_id(d["slot_id"], tenant_b.id)
        assert result is None

    async def test_list_by_materia(self, db_session, seed_slot_repo):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_materia(d["materia_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.materia_id == d["materia_id"] for r in results)

    async def test_list_by_materia_wrong_tenant(self, db_session, seed_slot_repo, tenant_b):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, tenant_b.id)
        results = await repo.list_by_materia(d["materia_id"], tenant_b.id)
        assert len(results) == 0

    async def test_list_by_asignacion(self, db_session, seed_slot_repo):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_asignacion(d["asig_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.asignacion_id == d["asig_id"] for r in results)

    async def test_soft_delete_slot(self, db_session, seed_slot_repo):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["slot_id"])
        await db_session.commit()

        result = await repo.get_by_id(d["slot_id"], d["tenant_a_id"])
        assert result is None

    async def test_create_slot(self, db_session, seed_slot_repo):
        d = seed_slot_repo
        repo = SlotEncuentroRepository(db_session, d["tenant_a_id"])
        nuevo = SlotEncuentro(
            titulo="Nuevo Slot", hora=time(10, 0),
            fecha_unica=date(2026, 5, 1), materia_id=d["materia_id"],
            asignacion_id=d["asig_id"],
        )
        result = await repo.create(nuevo)
        assert result.id is not None
        assert result.tenant_id == d["tenant_a_id"]
