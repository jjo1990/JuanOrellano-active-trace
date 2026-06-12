"""Tests para AnalisisService — reportes rapidos (C-11)."""

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


async def _semilla_reportes(db_session, tenant):
    carrera = Carrera(codigo="CARR-REP", nombre="CarreraReportes", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-REP", nombre="MateriaReportes", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-REP", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="repuser@test.com", password_hash=hash_password("pass123!"),
        nombre="Docente", apellidos="Reportes", tenant_id=tenant.id,
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
        nombre="Pedro", apellidos="Garcia", comision="A", regional="Centro",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    return entrada, materia, version


async def _agregar_cal_rep(db_session, tenant, entrada, materia, actividad, nota_numerica=None, nota_textual=None):
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


async def _agregar_entrada_rep(db_session, tenant, version, nombre, apellidos):
    entrada = EntradaPadron(
        tenant_id=tenant.id, version_id=version.id,
        nombre=nombre, apellidos=apellidos,
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(entrada)
    return entrada


@pytest.mark.needs_db
class TestReportes:
    async def test_reportes_metricas_basicas(self, db_session, tenant_a):
        entrada, materia, version = await _semilla_reportes(db_session, tenant_a)
        entrada2 = await _agregar_entrada_rep(db_session, tenant_a, version, "Lucia", "Diaz")

        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)
        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=60)
        await _agregar_cal_rep(db_session, tenant_a, entrada2, materia, "TP1", nota_numerica=45)
        await _agregar_cal_rep(db_session, tenant_a, entrada2, materia, "TP2", nota_numerica=70)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_reportes(materia.id)

        assert result.materia_id == materia.id
        assert result.total_alumnos == 2
        assert result.total_actividades == 2
        assert result.aprobacion_general == 75.0

    async def test_reportes_sin_calificaciones(self, db_session, tenant_a):
        _, materia, _ = await _semilla_reportes(db_session, tenant_a)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_reportes(materia.id)

        assert result.total_actividades == 0
        assert result.status_info is not None
        assert "Sin datos" in result.status_info

    async def test_reportes_actividad_dificil_facil(self, db_session, tenant_a):
        entrada, materia, _ = await _semilla_reportes(db_session, tenant_a)

        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP_Dificil", nota_numerica=30)
        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP_Facil", nota_numerica=90)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_reportes(materia.id)

        assert result.actividad_mas_dificil == "TP_Dificil"
        assert result.actividad_mas_facil == "TP_Facil"

    async def test_reportes_distribucion_notas(self, db_session, tenant_a):
        entrada, materia, _ = await _semilla_reportes(db_session, tenant_a)

        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=50)
        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=65)
        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP3", nota_numerica=75)
        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP4", nota_numerica=85)
        await _agregar_cal_rep(db_session, tenant_a, entrada, materia, "TP5", nota_numerica=95)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_reportes(materia.id)

        assert result.distribucion_notas["0-59"] == 1
        assert result.distribucion_notas["60-69"] == 1
        assert result.distribucion_notas["70-79"] == 1
        assert result.distribucion_notas["80-89"] == 1
        assert result.distribucion_notas["90-100"] == 1

    async def test_reportes_alumnos_al_dia(self, db_session, tenant_a):
        entrada, materia, version = await _semilla_reportes(db_session, tenant_a)
        entrada2 = await _agregar_entrada_rep(db_session, tenant_a, version, "Marta", "Ruiz")

        for act in ["TP1", "TP2"]:
            await _agregar_cal_rep(db_session, tenant_a, entrada, materia, act, nota_numerica=80)
        await _agregar_cal_rep(db_session, tenant_a, entrada2, materia, "TP1", nota_numerica=40)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_reportes(materia.id)

        assert result.alumnos_al_dia == 1
        assert result.alumnos_atrasados == 1

    async def test_reportes_tenant_isolation(self, db_session, tenant_a, tenant_b):
        entrada_a, materia_a, _ = await _semilla_reportes(db_session, tenant_a)

        carrera_b = Carrera(codigo="REP-B", nombre="RepB", tenant_id=tenant_b.id)
        db_session.add(carrera_b)
        await db_session.flush()
        materia_b = Materia(codigo="REP-MAT-B", nombre="RepMatB", tenant_id=tenant_b.id)
        db_session.add(materia_b)
        await db_session.flush()
        cohorte_b = Cohorte(
            carrera_id=carrera_b.id, nombre="2026-RB", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_b.id, activa=True,
        )
        db_session.add(cohorte_b)
        await db_session.flush()
        user_b = User(
            email="repb@test.com", password_hash=hash_password("pass123!"),
            nombre="B", apellidos="Rep", tenant_id=tenant_b.id,
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
            nombre="X", apellidos="Y",
        )
        db_session.add(entrada_b)
        await db_session.commit()

        await _agregar_cal_rep(db_session, tenant_a, entrada_a, materia_a, "TP1", nota_numerica=70)
        await _agregar_cal_rep(db_session, tenant_b, entrada_b, materia_b, "TP1", nota_numerica=90)

        svc_a = AnalisisService(db_session, tenant_a.id)
        result = await svc_a.get_reportes(materia_a.id)

        assert result.total_alumnos == 1
