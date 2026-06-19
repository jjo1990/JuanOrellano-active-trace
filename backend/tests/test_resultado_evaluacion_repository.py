"""TDD tests for ResultadoEvaluacionRepository."""

import uuid
from datetime import date

import pytest

from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.evaluacion import Evaluacion
from app.models.materia import Materia
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.user import User
from app.repositories.resultado_evaluacion_repository import ResultadoEvaluacionRepository


@pytest.fixture
async def seed_resultado_repo(db_session, tenant_a):
    user = User(
        email="resultadorepo@test.com", password_hash="hash",
        nombre="Alumno", apellidos="Resultado", tenant_id=tenant_a.id,
        legajo="L-RES",
    )
    db_session.add(user)
    await db_session.flush()

    materia = Materia(codigo="MAT_RES", nombre="Materia RES", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(nombre="Carrera RES", codigo="CAR_RES", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="Cohorte RES",
        anio=2026, vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    evaluacion = Evaluacion(
        materia_id=materia.id, cohorte_id=cohorte.id,
        tipo="Coloquio", instancia="Coloquio RES",
        dias_disponibles=3, cupos_por_dia=5, estado="Activa",
        tenant_id=tenant_a.id,
    )
    db_session.add(evaluacion)
    await db_session.flush()

    resultado = ResultadoEvaluacion(
        evaluacion_id=evaluacion.id, alumno_id=user.id,
        nota_final=None, tenant_id=tenant_a.id,
    )
    db_session.add(resultado)
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user_id": user.id,
        "materia_id": materia.id,
        "cohorte_id": cohorte.id,
        "evaluacion_id": evaluacion.id,
        "resultado_id": resultado.id,
    }


@pytest.mark.needs_db
class TestResultadoEvaluacionRepository:
    async def test_get_by_id_returns_resultado(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_id(d["resultado_id"], d["tenant_a_id"])
        assert result is not None
        assert result.nota_final is None

    async def test_list_by_evaluacion(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_evaluacion(d["evaluacion_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.evaluacion_id == d["evaluacion_id"] for r in results)

    async def test_get_by_alumno_evaluacion(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_alumno_evaluacion(d["evaluacion_id"], d["user_id"])
        assert result is not None
        assert result.alumno_id == d["user_id"]

    async def test_get_by_alumno_evaluacion_no_existe(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_alumno_evaluacion(d["evaluacion_id"], uuid.uuid4())
        assert result is None

    async def test_list_pendientes(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_pendientes(d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.nota_final is None for r in results)

    async def test_update_nota(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        resultado = await repo.get_by_id(d["resultado_id"], d["tenant_a_id"])
        assert resultado is not None
        resultado.nota_final = "8"
        await db_session.flush()

        actualizado = await repo.get_by_id(d["resultado_id"], d["tenant_a_id"])
        assert actualizado is not None
        assert actualizado.nota_final == "8"

    async def test_soft_delete_resultado(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["resultado_id"])
        await db_session.commit()

        result = await repo.get_by_id(d["resultado_id"], d["tenant_a_id"])
        assert result is None

    async def test_create_resultado(self, db_session, seed_resultado_repo):
        d = seed_resultado_repo
        repo = ResultadoEvaluacionRepository(db_session, d["tenant_a_id"])
        # Create a new evaluation to avoid unique constraint
        nueva_eval = Evaluacion(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="TP", instancia="TP Test", dias_disponibles=1,
            cupos_por_dia=2, estado="Activa", tenant_id=d["tenant_a_id"],
        )
        db_session.add(nueva_eval)
        await db_session.flush()

        nuevo = ResultadoEvaluacion(
            evaluacion_id=nueva_eval.id, alumno_id=d["user_id"],
            nota_final=None,
        )
        result = await repo.create(nuevo)
        assert result.id is not None
        assert result.tenant_id == d["tenant_a_id"]
        assert result.nota_final is None
