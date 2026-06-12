"""Tests para AnalisisService — ranking de aprobadas (C-11)."""

from datetime import date

import pytest

from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.core.security import hash_password
from app.services.analisis_service import AnalisisService


async def _semilla_ranking(db_session, tenant):
    carrera = Carrera(codigo="CARR-RNK", nombre="CarreraRanking", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-RNK", nombre="MateriaRanking", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-R", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="rnkuser@test.com", password_hash=hash_password("pass123!"),
        nombre="Docente", apellidos="Ranking", tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.flush()
    version = VersionPadron(
        tenant_id=tenant.id, materia_id=materia.id, cohorte_id=cohorte.id,
        cargado_por=user.id, activa=True,
    )
    db_session.add(version)
    await db_session.flush()
    entrada = EntradaPadron(
        tenant_id=tenant.id, version_id=version.id,
        nombre="Ana", apellidos="Lopez", comision="A", regional="Centro",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    return entrada, materia, version


async def _agregar_entrada_ranking(db_session, tenant, version, nombre, apellidos):
    entrada = EntradaPadron(
        tenant_id=tenant.id, version_id=version.id,
        nombre=nombre, apellidos=apellidos,
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(entrada)
    return entrada


async def _agregar_cal(db_session, tenant, entrada, materia, actividad, nota_numerica=None, nota_textual=None):
    cal = Calificacion(
        tenant_id=tenant.id,
        entrada_padron_id=entrada.id,
        materia_id=materia.id,
        actividad=actividad,
        nota_numerica=nota_numerica,
        nota_textual=nota_textual,
        origen="Importado",
    )
    db_session.add(cal)
    await db_session.commit()
    await db_session.refresh(cal)
    return cal


@pytest.mark.needs_db
class TestRanking:
    async def test_ranking_orden_descendente(self, db_session, tenant_a):
        entrada_a, materia, version = await _semilla_ranking(db_session, tenant_a)
        entrada_b = await _agregar_entrada_ranking(db_session, tenant_a, version, "Beto", "Martinez")
        entrada_c = await _agregar_entrada_ranking(db_session, tenant_a, version, "Carlos", "Ruiz")
        entrada_d = await _agregar_entrada_ranking(db_session, tenant_a, version, "Diana", "Sosa")

        for act in ["TP1", "TP2", "TP3", "TP4"]:
            await _agregar_cal(db_session, tenant_a, entrada_a, materia, act, nota_numerica=70)
        for act in ["TP1", "TP2"]:
            await _agregar_cal(db_session, tenant_a, entrada_b, materia, act, nota_numerica=70)
        for act in ["TP1", "TP2", "TP3", "TP4"]:
            await _agregar_cal(db_session, tenant_a, entrada_c, materia, act, nota_numerica=70)
        await _agregar_cal(db_session, tenant_a, entrada_d, materia, "TP1", nota_numerica=45)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_ranking(materia.id)

        assert result.materia_id == materia.id
        assert result.total_alumnos == 4
        assert len(result.ranking) == 3
        assert result.ranking[0].aprobadas == 4
        assert result.ranking[0].porcentaje == 100.0
        assert result.ranking[2].aprobadas == 2

    async def test_ranking_excluye_cero_aprobadas(self, db_session, tenant_a):
        entrada, materia, version = await _semilla_ranking(db_session, tenant_a)

        await _agregar_cal(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=45)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_ranking(materia.id)

        assert len(result.ranking) == 0
        assert result.status_info is not None

    async def test_ranking_todos_excluidos_sin_aprobadas(self, db_session, tenant_a):
        entrada, materia, version = await _semilla_ranking(db_session, tenant_a)
        entrada_b = await _agregar_entrada_ranking(db_session, tenant_a, version, "Beto", "Martinez")

        await _agregar_cal(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=45)
        await _agregar_cal(db_session, tenant_a, entrada_b, materia, "TP1", nota_numerica=30)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_ranking(materia.id)

        assert len(result.ranking) == 0
        assert result.status_info is not None

    async def test_ranking_textual_satisfactorio_cuenta(self, db_session, tenant_a):
        entrada, materia, _ = await _semilla_ranking(db_session, tenant_a)

        await _agregar_cal(db_session, tenant_a, entrada, materia, "TP1", nota_textual="Satisfactorio")

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_ranking(materia.id)

        assert len(result.ranking) == 1
        assert result.ranking[0].aprobadas == 1

    async def test_ranking_default_umbral(self, db_session, tenant_a):
        entrada, materia, version = await _semilla_ranking(db_session, tenant_a)

        await _agregar_cal(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=60)
        await _agregar_cal(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=59)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_ranking(materia.id)

        assert len(result.ranking) == 1
        assert result.ranking[0].aprobadas == 1

    async def test_ranking_tenant_isolation(self, db_session, tenant_a, tenant_b):
        entrada_a, materia_a, version_a = await _semilla_ranking(db_session, tenant_a)

        carrera_b = Carrera(codigo="RNK-B", nombre="RankingB", tenant_id=tenant_b.id)
        db_session.add(carrera_b)
        await db_session.flush()
        materia_b = Materia(codigo="RNK-MAT-B", nombre="RankMatB", tenant_id=tenant_b.id)
        db_session.add(materia_b)
        await db_session.flush()
        cohorte_b = Cohorte(
            carrera_id=carrera_b.id, nombre="2026-RB", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_b.id, activa=True,
        )
        db_session.add(cohorte_b)
        await db_session.flush()
        user_b = User(
            email="rnkb@test.com", password_hash=hash_password("pass123!"),
            nombre="B", apellidos="Rank", tenant_id=tenant_b.id,
        )
        db_session.add(user_b)
        await db_session.flush()
        version_b = VersionPadron(
            tenant_id=tenant_b.id, materia_id=materia_b.id, cohorte_id=cohorte_b.id,
            cargado_por=user_b.id, activa=True,
        )
        db_session.add(version_b)
        await db_session.flush()
        entrada_b = EntradaPadron(
            tenant_id=tenant_b.id, version_id=version_b.id,
            nombre="Zeta", apellidos="Ultimo",
        )
        db_session.add(entrada_b)
        await db_session.commit()

        await _agregar_cal(db_session, tenant_a, entrada_a, materia_a, "TP1", nota_numerica=70)
        await _agregar_cal(db_session, tenant_b, entrada_b, materia_b, "TP1", nota_numerica=90)

        svc_a = AnalisisService(db_session, tenant_a.id)
        result = await svc_a.get_ranking(materia_a.id)

        assert result.total_alumnos == 1
        assert len(result.ranking) == 1
