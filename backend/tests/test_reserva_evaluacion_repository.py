"""TDD tests for ReservaEvaluacionRepository."""

import uuid
from datetime import date, datetime, timezone

import pytest

from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.evaluacion import Evaluacion
from app.models.materia import Materia
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.user import User
from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository


@pytest.fixture
async def seed_reserva_repo(db_session, tenant_a):
    user = User(
        email="reservarepo@test.com", password_hash="hash",
        nombre="Alumno", apellidos="Repo", tenant_id=tenant_a.id,
        legajo="L-RR",
    )
    db_session.add(user)
    await db_session.flush()

    materia = Materia(codigo="MAT_RR", nombre="Materia RR", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(nombre="Carrera RR", codigo="CAR_RR", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="Cohorte RR",
        anio=2026, vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    evaluacion = Evaluacion(
        materia_id=materia.id, cohorte_id=cohorte.id,
        tipo="Coloquio", instancia="Coloquio RR",
        dias_disponibles=3, cupos_por_dia=5, estado="Activa",
        tenant_id=tenant_a.id,
    )
    db_session.add(evaluacion)
    await db_session.flush()

    reserva = ReservaEvaluacion(
        evaluacion_id=evaluacion.id, alumno_id=user.id,
        fecha_hora=datetime(2026, 6, 20, 14, 0, tzinfo=timezone.utc),
        estado="Activa", tenant_id=tenant_a.id,
    )
    db_session.add(reserva)
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user_id": user.id,
        "materia_id": materia.id,
        "cohorte_id": cohorte.id,
        "evaluacion_id": evaluacion.id,
        "reserva_id": reserva.id,
    }


@pytest.mark.needs_db
class TestReservaEvaluacionRepository:
    async def test_get_by_id_returns_reserva(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_id(d["reserva_id"], d["tenant_a_id"])
        assert result is not None
        assert result.estado == "Activa"
        assert result.alumno_id == d["user_id"]

    async def test_list_by_evaluacion(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_evaluacion(d["evaluacion_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.evaluacion_id == d["evaluacion_id"] for r in results)

    async def test_list_by_evaluacion_filtra_estado(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_evaluacion(
            d["evaluacion_id"], d["tenant_a_id"], estado="Activa",
        )
        assert len(results) >= 1
        assert all(r.estado == "Activa" for r in results)

        results_cancel = await repo.list_by_evaluacion(
            d["evaluacion_id"], d["tenant_a_id"], estado="Cancelada",
        )
        assert len(results_cancel) == 0

    async def test_list_by_alumno(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_alumno(d["user_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.alumno_id == d["user_id"] for r in results)

    async def test_count_activas_por_fecha(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        count = await repo.count_activas_por_fecha(
            d["evaluacion_id"], datetime(2026, 6, 20, 14, 0, tzinfo=timezone.utc),
        )
        assert count == 1

    async def test_count_activas_por_fecha_cero_sin_reservas(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        count = await repo.count_activas_por_fecha(
            d["evaluacion_id"], datetime(2026, 6, 21, 14, 0, tzinfo=timezone.utc),
        )
        assert count == 0

    async def test_get_activa_por_alumno_evaluacion(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_activa_por_alumno_evaluacion(
            d["evaluacion_id"], d["user_id"],
        )
        assert result is not None
        assert result.estado == "Activa"

    async def test_get_activa_por_alumno_evaluacion_no_existe(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_activa_por_alumno_evaluacion(
            d["evaluacion_id"], uuid.uuid4(),
        )
        assert result is None

    async def test_cancelar_reserva(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.cancelar(d["reserva_id"])
        assert result is not None
        assert result.estado == "Cancelada"
        await db_session.commit()

        activa = await repo.get_activa_por_alumno_evaluacion(
            d["evaluacion_id"], d["user_id"],
        )
        assert activa is None

    async def test_soft_delete_reserva(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["reserva_id"])
        await db_session.commit()

        result = await repo.get_by_id(d["reserva_id"], d["tenant_a_id"])
        assert result is None

    async def test_create_reserva(self, db_session, seed_reserva_repo):
        d = seed_reserva_repo
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        nueva = ReservaEvaluacion(
            evaluacion_id=d["evaluacion_id"], alumno_id=d["user_id"],
            fecha_hora=datetime(2026, 6, 21, 10, 0, tzinfo=timezone.utc),
            estado="Activa",
        )
        # Need a different alumno or evaluation for the fixture since we already have one
        user2 = User(
            email="reservarepo2@test.com", password_hash="hash",
            nombre="Alumno2", apellidos="Repo", tenant_id=d["tenant_a_id"],
            legajo="L-RR2",
        )
        db_session.add(user2)
        await db_session.flush()
        nueva.alumno_id = user2.id
        result = await repo.create(nueva)
        assert result.id is not None
        assert result.tenant_id == d["tenant_a_id"]
