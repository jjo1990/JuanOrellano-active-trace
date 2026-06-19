"""TDD tests for InstanciaEncuentroRepository."""

import uuid
from datetime import date, time

import pytest

from app.models.asignacion import Asignacion
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.slot_encuentro import SlotEncuentro
from app.models.user import User
from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository


@pytest.fixture
async def seed_instancia_repo(db_session, tenant_a):
    user = User(
        email="instrepo@test.com", password_hash="hash",
        nombre="Inst", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-011",
    )
    db_session.add(user)
    await db_session.flush()

    rol = Rol(nombre="PROFESOR_INST", descripcion="Prof Inst", tenant_id=tenant_a.id)
    db_session.add(rol)
    await db_session.flush()

    materia = Materia(codigo="MAT_INST", nombre="Materia Inst", activa=True, tenant_id=tenant_a.id)
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
        titulo="Slot con instancias", hora=time(18, 0),
        dia_semana="Lunes", fecha_inicio=date(2026, 3, 9),
        cant_semanas=4, materia_id=materia.id, asignacion_id=asig.id,
        tenant_id=tenant_a.id,
    )
    db_session.add(slot)
    await db_session.flush()

    inst1 = InstanciaEncuentro(
        slot_id=slot.id, materia_id=materia.id,
        fecha=date(2026, 3, 9), hora=time(18, 0),
        titulo="Clase 1", estado="Programado",
        tenant_id=tenant_a.id,
    )
    inst2 = InstanciaEncuentro(
        slot_id=slot.id, materia_id=materia.id,
        fecha=date(2026, 3, 16), hora=time(18, 0),
        titulo="Clase 2", estado="Realizado",
        meet_url="https://meet.google.com/abc",
        tenant_id=tenant_a.id,
    )
    inst3 = InstanciaEncuentro(
        slot_id=slot.id, materia_id=materia.id,
        fecha=date(2026, 3, 23), hora=time(18, 0),
        titulo="Clase 3", estado="Programado",
        tenant_id=tenant_a.id,
    )
    db_session.add_all([inst1, inst2, inst3])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "materia_id": materia.id,
        "asig_id": asig.id,
        "slot_id": slot.id,
        "inst1_id": inst1.id,
        "inst2_id": inst2.id,
        "inst3_id": inst3.id,
    }


@pytest.mark.needs_db
class TestInstanciaEncuentroRepository:
    async def test_list_by_slot_ordenadas_por_fecha(self, db_session, seed_instancia_repo):
        d = seed_instancia_repo
        repo = InstanciaEncuentroRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_slot(d["slot_id"], d["tenant_a_id"])
        assert len(results) == 3
        assert results[0].fecha == date(2026, 3, 9)
        assert results[1].fecha == date(2026, 3, 16)
        assert results[2].fecha == date(2026, 3, 23)

    async def test_list_by_slot_wrong_tenant(self, db_session, seed_instancia_repo, tenant_b):
        d = seed_instancia_repo
        repo = InstanciaEncuentroRepository(db_session, tenant_b.id)
        results = await repo.list_by_slot(d["slot_id"], tenant_b.id)
        assert len(results) == 0

    async def test_list_by_materia_with_filters(self, db_session, seed_instancia_repo):
        d = seed_instancia_repo
        repo = InstanciaEncuentroRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_materia(d["materia_id"], d["tenant_a_id"], estado="Programado")
        assert len(results) == 2
        assert all(r.estado == "Programado" for r in results)

    async def test_list_by_fecha_range(self, db_session, seed_instancia_repo):
        d = seed_instancia_repo
        repo = InstanciaEncuentroRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_fecha_range(
            d["tenant_a_id"], date(2026, 3, 10), date(2026, 3, 30),
        )
        assert len(results) == 2
        fechas = [r.fecha for r in results]
        assert date(2026, 3, 9) not in fechas

    async def test_list_independientes(self, db_session, seed_instancia_repo):
        d = seed_instancia_repo
        repo = InstanciaEncuentroRepository(db_session, d["tenant_a_id"])
        independiente = InstanciaEncuentro(
            slot_id=None, materia_id=d["materia_id"],
            fecha=date(2026, 5, 1), hora=time(14, 0),
            titulo="Consulta ad-hoc", estado="Programado",
            tenant_id=d["tenant_a_id"],
        )
        db_session.add(independiente)
        await db_session.commit()

        results = await repo.list_independientes(d["tenant_a_id"], d["materia_id"])
        assert len(results) == 1
        assert results[0].slot_id is None

    async def test_soft_delete_instancia(self, db_session, seed_instancia_repo):
        d = seed_instancia_repo
        repo = InstanciaEncuentroRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["inst1_id"])
        await db_session.commit()

        results = await repo.list_by_slot(d["slot_id"], d["tenant_a_id"])
        ids = [r.id for r in results]
        assert d["inst1_id"] not in ids
        assert len(results) == 2
