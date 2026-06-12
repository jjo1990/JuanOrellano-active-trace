"""Tests para AnalisisService — deteccion de atrasados (C-11)."""

from datetime import date

import pytest

from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.core.security import hash_password
from app.services.analisis_service import AnalisisService


async def _semilla_atrasados(db_session, tenant):
    carrera = Carrera(codigo="CARR-ATR", nombre="CarreraAtrasados", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-ATR", nombre="MateriaAtrasados", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-A", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="atruser@test.com", password_hash=hash_password("pass123!"),
        nombre="Docente", apellidos="Atrasados", tenant_id=tenant.id,
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
        nombre="Juan", apellidos="Perez", comision="A", regional="Centro",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    await db_session.refresh(user)
    return entrada, materia, user, version


async def _agregar_entrada(db_session, tenant, version, nombre, apellidos, comision="A", regional="Centro"):
    entrada = EntradaPadron(
        tenant_id=tenant.id, version_id=version.id,
        nombre=nombre, apellidos=apellidos, comision=comision, regional=regional,
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(entrada)
    return entrada


async def _agregar_calificacion(db_session, tenant, entrada, materia, actividad, nota_numerica=None, nota_textual=None):
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
class TestAtrasados:
    async def test_atrasado_por_actividades_faltantes(self, db_session, tenant_a):
        entrada, materia, _, version = await _semilla_atrasados(db_session, tenant_a)
        entrada2 = await _agregar_entrada(db_session, tenant_a, version, "Ana", "Lopez")

        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=75)
        await _agregar_calificacion(db_session, tenant_a, entrada2, materia, "TP1", nota_numerica=80)
        await _agregar_calificacion(db_session, tenant_a, entrada2, materia, "TP2", nota_numerica=90)
        await _agregar_calificacion(db_session, tenant_a, entrada2, materia, "TP3", nota_numerica=85)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert result.materia_id == materia.id
        assert result.total_alumnos == 2
        assert result.total_atrasados == 1
        a = result.atrasados[0]
        assert a.entrada_padron_id == entrada.id
        assert "TP2" in a.actividades_faltantes
        assert "TP3" in a.actividades_faltantes
        assert "TP1" not in a.actividades_faltantes

    async def test_atrasado_por_nota_bajo_umbral(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_atrasados(db_session, tenant_a)

        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=45)
        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=70)
        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP3", nota_numerica=80)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert len(result.atrasados) == 1
        alumno = result.atrasados[0]
        assert len(alumno.notas_bajas) == 1
        assert alumno.notas_bajas[0].actividad == "TP1"
        assert alumno.notas_bajas[0].nota == 45

    async def test_atrasado_por_textual_no_aprobatoria(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_atrasados(db_session, tenant_a)

        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP1", nota_textual="Regular")
        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP2", nota_textual="Satisfactorio")

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert len(result.atrasados) == 1
        alumno = result.atrasados[0]
        assert len(alumno.notas_bajas) == 1
        assert alumno.notas_bajas[0].actividad == "TP1"
        assert alumno.notas_bajas[0].nota_textual == "Regular"

    async def test_sin_calificaciones_es_atrasado(self, db_session, tenant_a):
        entrada, materia, _, version = await _semilla_atrasados(db_session, tenant_a)
        entrada2 = await _agregar_entrada(db_session, tenant_a, version, "Ana", "Lopez")

        await _agregar_calificacion(db_session, tenant_a, entrada2, materia, "TP1", nota_numerica=75)
        await _agregar_calificacion(db_session, tenant_a, entrada2, materia, "TP2", nota_numerica=80)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert len(result.atrasados) == 1
        a = result.atrasados[0]
        assert a.entrada_padron_id == entrada.id
        assert "TP1" in a.actividades_faltantes
        assert "TP2" in a.actividades_faltantes

    async def test_alumno_al_dia_no_atrasado(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_atrasados(db_session, tenant_a)

        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=75)
        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=80)
        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP3", nota_numerica=90)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert result.total_atrasados == 0
        assert len(result.atrasados) == 0

    async def test_sin_calificaciones_status_info(self, db_session, tenant_a):
        _, materia, _, _ = await _semilla_atrasados(db_session, tenant_a)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert result.total_atrasados == 0
        assert result.status_info is not None
        assert "Sin datos" in result.status_info

    async def test_umbral_por_defecto(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_atrasados(db_session, tenant_a)

        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=60)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert result.total_atrasados == 0
        assert result.atrasados == []

    async def test_tenant_isolation(self, db_session, tenant_a, tenant_b):
        entrada_a, materia_a, _, version_a = await _semilla_atrasados(db_session, tenant_a)

        carrera_b = Carrera(codigo="CARR-B", nombre="CarreraB", tenant_id=tenant_b.id)
        db_session.add(carrera_b)
        await db_session.flush()
        materia_b = Materia(codigo="MAT-B", nombre="MateriaB", tenant_id=tenant_b.id)
        db_session.add(materia_b)
        await db_session.flush()
        cohorte_b = Cohorte(
            carrera_id=carrera_b.id, nombre="2026-B", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_b.id, activa=True,
        )
        db_session.add(cohorte_b)
        await db_session.flush()
        user_b = User(
            email="buser@test.com", password_hash=hash_password("pass123!"),
            nombre="B", apellidos="User", tenant_id=tenant_b.id,
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
            nombre="Maria", apellidos="Gomez",
        )
        db_session.add(entrada_b)
        await db_session.commit()

        await _agregar_calificacion(db_session, tenant_a, entrada_a, materia_a, "TP1", nota_numerica=45)
        await _agregar_calificacion(db_session, tenant_b, entrada_b, materia_b, "TP1", nota_numerica=90)

        svc_a = AnalisisService(db_session, tenant_a.id)
        result = await svc_a.get_atrasados(materia_a.id)

        assert result.total_alumnos == 1
        assert len(result.atrasados) == 1

    async def test_atrasado_con_nota_baja_y_faltantes(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_atrasados(db_session, tenant_a)

        await _agregar_calificacion(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=40)

        svc = AnalisisService(db_session, tenant_a.id)
        result = await svc.get_atrasados(materia.id)

        assert len(result.atrasados) == 1
        a = result.atrasados[0]
        assert len(a.notas_bajas) == 1
        assert len(a.actividades_faltantes) == 0
