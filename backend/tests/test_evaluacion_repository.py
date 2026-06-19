"""TDD tests for EvaluacionRepository."""

import uuid
from datetime import date

import pytest

from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.evaluacion import Evaluacion
from app.models.materia import Materia
from app.repositories.evaluacion_repository import EvaluacionRepository


@pytest.fixture
async def seed_evaluacion_repo(db_session, tenant_a):
    materia = Materia(codigo="MAT_EVAL", nombre="Materia Eval", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(nombre="Carrera Eval", codigo="CAR_EVAL", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="Cohorte Eval",
        anio=2026, vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    evaluacion = Evaluacion(
        materia_id=materia.id, cohorte_id=cohorte.id,
        tipo="Coloquio", instancia="Coloquio Final",
        dias_disponibles=3, cupos_por_dia=5, estado="Activa",
        tenant_id=tenant_a.id,
    )
    db_session.add(evaluacion)
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "materia_id": materia.id,
        "cohorte_id": cohorte.id,
        "evaluacion_id": evaluacion.id,
    }


@pytest.mark.needs_db
class TestEvaluacionRepository:
    async def test_get_by_id_returns_evaluacion(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_id(d["evaluacion_id"], d["tenant_a_id"])
        assert result is not None
        assert result.tipo == "Coloquio"
        assert result.estado == "Activa"

    async def test_get_by_id_wrong_tenant_returns_none(self, db_session, seed_evaluacion_repo, tenant_b):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, tenant_b.id)
        result = await repo.get_by_id(d["evaluacion_id"], tenant_b.id)
        assert result is None

    async def test_list_by_materia(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_materia(d["materia_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.materia_id == d["materia_id"] for r in results)

    async def test_list_by_materia_wrong_tenant(self, db_session, seed_evaluacion_repo, tenant_b):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, tenant_b.id)
        results = await repo.list_by_materia(d["materia_id"], tenant_b.id)
        assert len(results) == 0

    async def test_list_by_cohorte(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_cohorte(d["cohorte_id"], d["tenant_a_id"])
        assert len(results) >= 1
        assert all(r.cohorte_id == d["cohorte_id"] for r in results)

    async def test_list_all_filter_by_estado(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_all(d["tenant_a_id"], estado="Activa")
        assert len(results) >= 1
        assert all(r.estado == "Activa" for r in results)

    async def test_list_empty_for_cerrada(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_all(d["tenant_a_id"], estado="Cerrada")
        assert len(results) == 0

    async def test_soft_delete_evaluacion(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["evaluacion_id"])
        await db_session.commit()

        result = await repo.get_by_id(d["evaluacion_id"], d["tenant_a_id"])
        assert result is None

    async def test_create_evaluacion(self, db_session, seed_evaluacion_repo):
        d = seed_evaluacion_repo
        repo = EvaluacionRepository(db_session, d["tenant_a_id"])
        nueva = Evaluacion(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Parcial", instancia="Parcial 1",
            dias_disponibles=2, cupos_por_dia=3, estado="Activa",
        )
        result = await repo.create(nueva)
        assert result.id is not None
        assert result.tenant_id == d["tenant_a_id"]
        assert result.tipo == "Parcial"
