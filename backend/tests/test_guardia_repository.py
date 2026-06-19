"""TDD tests for GuardiaRepository."""

import uuid
from datetime import date

import pytest

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.guardia import Guardia
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.repositories.guardia_repository import GuardiaRepository


@pytest.fixture
async def seed_guardia_repo(db_session, tenant_a):
    user = User(
        email="guardiarepo@test.com", password_hash="hash",
        nombre="Tutor", apellidos="Guardia", tenant_id=tenant_a.id,
        legajo="L-012",
    )
    db_session.add(user)
    await db_session.flush()

    rol = Rol(nombre="TUTOR_GUARDIA", descripcion="Tutor Guardia", tenant_id=tenant_a.id)
    db_session.add(rol)
    await db_session.flush()

    materia = Materia(codigo="MAT_GUARDIA", nombre="Materia Guardia", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(codigo="CAR_GUARDIA", nombre="Carrera Guardia", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="COH_GUARDIA", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    asig = Asignacion(
        usuario_id=user.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    db_session.add(asig)
    await db_session.flush()

    guardia1 = Guardia(
        asignacion_id=asig.id, materia_id=materia.id,
        carrera_id=carrera.id, cohorte_id=cohorte.id,
        dia="Lunes", horario="14:00–14:45", estado="Realizada",
        comentarios="Todo OK", tenant_id=tenant_a.id,
    )
    guardia2 = Guardia(
        asignacion_id=asig.id, materia_id=materia.id,
        carrera_id=carrera.id, cohorte_id=cohorte.id,
        dia="Martes", horario="15:00–15:45", estado="Pendiente",
        tenant_id=tenant_a.id,
    )
    db_session.add_all([guardia1, guardia2])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user_id": user.id,
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "asig_id": asig.id,
        "guardia1_id": guardia1.id,
        "guardia2_id": guardia2.id,
    }


@pytest.mark.needs_db
class TestGuardiaRepository:
    async def test_list_by_materia(self, db_session, seed_guardia_repo):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_materia(d["materia_id"], d["tenant_a_id"])
        assert len(results) == 2

    async def test_list_by_materia_wrong_tenant(self, db_session, seed_guardia_repo, tenant_b):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, tenant_b.id)
        results = await repo.list_by_materia(d["materia_id"], tenant_b.id)
        assert len(results) == 0

    async def test_list_by_asignacion(self, db_session, seed_guardia_repo):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_asignacion(d["asig_id"], d["tenant_a_id"])
        assert len(results) == 2

    async def test_list_with_filters_by_estado(self, db_session, seed_guardia_repo):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_filters(
            d["tenant_a_id"], estado="Pendiente",
        )
        assert len(results) == 1
        assert results[0].estado == "Pendiente"

    async def test_list_with_filters_combined(self, db_session, seed_guardia_repo):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_filters(
            d["tenant_a_id"],
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            estado="Realizada",
        )
        assert len(results) == 1
        assert results[0].estado == "Realizada"

    async def test_list_with_filters_empty_for_wrong_tenant(self, db_session, seed_guardia_repo, tenant_b):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, tenant_b.id)
        results = await repo.list_with_filters(
            tenant_b.id, materia_id=d["materia_id"],
        )
        assert len(results) == 0

    async def test_soft_delete_guardia(self, db_session, seed_guardia_repo):
        d = seed_guardia_repo
        repo = GuardiaRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["guardia1_id"])
        await db_session.commit()

        results = await repo.list_by_materia(d["materia_id"], d["tenant_a_id"])
        ids = [r.id for r in results]
        assert d["guardia1_id"] not in ids
        assert len(results) == 1
