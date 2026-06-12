"""Tests para AnalisisService — monitor, seguimiento, admin, notas-finales, sin-corregir (C-11)."""

from datetime import date, datetime, timezone

import pytest

from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.models.asignacion import Asignacion
from app.models.rol import Rol
from app.core.security import hash_password
from app.services.monitor_service import MonitorService
from app.services.calificaciones_service import CalificacionesService


async def _semilla_monitor(db_session, tenant):
    carrera = Carrera(codigo="CARR-MON", nombre="CarreraMonitor", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-MON", nombre="MateriaMonitor", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-MON", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="monuser@test.com", password_hash=hash_password("pass123!"),
        nombre="Docente", apellidos="Monitor", tenant_id=tenant.id,
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
        nombre="Luis", apellidos="Paz", comision="A", regional="Norte",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    await db_session.refresh(user)
    return entrada, materia, version, user


async def _agregar_entrada_mon(db_session, tenant, version, nombre, apellidos, comision="A", regional="Norte"):
    entrada = EntradaPadron(
        tenant_id=tenant.id, version_id=version.id,
        nombre=nombre, apellidos=apellidos, comision=comision, regional=regional,
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(entrada)
    return entrada


async def _agregar_cal_mon(db_session, tenant, entrada, materia, actividad, nota_numerica=None, nota_textual=None, importado_at=None):
    cal = Calificacion(
        tenant_id=tenant.id,
        entrada_padron_id=entrada.id,
        materia_id=materia.id,
        actividad=actividad,
        nota_numerica=nota_numerica,
        nota_textual=nota_textual,
        origen="Importado",
    )
    if importado_at is not None:
        cal.importado_at = importado_at
    db_session.add(cal)
    await db_session.commit()
    await db_session.refresh(cal)
    return cal


@pytest.mark.needs_db
class TestMonitorGeneral:
    async def test_monitor_devuelve_todos_estudiantes(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Ana", "Sosa")

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor(materia_id=materia.id)

        assert result.total == 2
        assert len(result.estudiantes) == 2

    async def test_monitor_filtra_por_materia(self, db_session, tenant_a):
        entrada, materia, version, user = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Ana", "Sosa")

        carrera2 = Carrera(codigo="MON-C2", nombre="MonC2", tenant_id=tenant_a.id)
        db_session.add(carrera2)
        await db_session.flush()
        materia2 = Materia(codigo="MON-MAT2", nombre="MonMat2", tenant_id=tenant_a.id)
        db_session.add(materia2)
        await db_session.flush()
        cohorte2 = Cohorte(
            carrera_id=carrera2.id, nombre="2026-M2", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
        )
        db_session.add(cohorte2)
        await db_session.flush()
        version2 = VersionPadron(
            tenant_id=tenant_a.id, materia_id=materia2.id, cohorte_id=cohorte2.id,
            cargado_por=user.id, activa=True,
        )
        db_session.add(version2)
        await db_session.flush()
        entrada3 = EntradaPadron(
            tenant_id=tenant_a.id, version_id=version2.id,
            nombre="Tomas", apellidos="Luna",
        )
        db_session.add(entrada3)
        await db_session.commit()

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)
        await _agregar_cal_mon(db_session, tenant_a, entrada3, materia2, "TP1", nota_numerica=70)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor(materia_id=materia.id)

        assert result.total == 2

    async def test_monitor_filtra_por_regional(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Ana", "Sosa", regional="Sur")

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor(materia_id=materia.id, regional="Sur")

        assert result.total == 1
        assert result.estudiantes[0].nombre == "Ana"

    async def test_monitor_filtra_por_estado(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=40)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=70)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor(materia_id=materia.id, estado="atrasado")

        assert result.total == 1

    async def test_monitor_busqueda_por_nombre(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Carlos", "Perez")

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor(materia_id=materia.id, alumno="Carlos")

        assert result.total == 1
        assert result.estudiantes[0].nombre == "Carlos"

    async def test_monitor_filtros_combinados(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Ana", "Sosa", comision="B", regional="Sur")

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=40)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=70)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor(
            materia_id=materia.id, regional="Norte", estado="atrasado",
        )

        assert result.total == 1
        assert result.estudiantes[0].nombre == "Luis"

    async def test_monitor_tenant_isolation(self, db_session, tenant_a, tenant_b):
        entrada_a, materia_a, _, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada_a, materia_a, "TP1", nota_numerica=80)

        svc_a = MonitorService(db_session, tenant_a.id)
        svc_b = MonitorService(db_session, tenant_b.id)
        result_a = await svc_a.get_monitor(materia_id=materia_a.id)
        result_b = await svc_b.get_monitor(materia_id=materia_a.id)

        assert result_a.total == 1
        assert result_b.total == 0


@pytest.mark.needs_db
class TestMonitorSeguimiento:
    async def test_seguimiento_solo_asignados(self, db_session, tenant_a):
        entrada, materia, version, user = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)

        rol = Rol(nombre="PROF_SEG", descripcion="Prof Seguimiento", tenant_id=tenant_a.id)
        db_session.add(rol)
        await db_session.flush()
        asign = Asignacion(
            tenant_id=tenant_a.id, usuario_id=user.id, rol_id=rol.id,
            materia_id=materia.id, desde=date(2026, 1, 1),
        )
        db_session.add(asign)
        await db_session.commit()

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor_seguimiento(user_id=user.id)

        assert result.total == 1
        assert result.estudiantes[0].materia_id == materia.id

    async def test_seguimiento_filtra_min_aprobadas(self, db_session, tenant_a):
        entrada, materia, version, user = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Beto", "Luna")

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=90)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP3", nota_numerica=85)
        await _agregar_cal_mon(db_session, tenant_a, entrada2, materia, "TP1", nota_numerica=70)

        rol = Rol(nombre="PROF_MIN", descripcion="Prof Min", tenant_id=tenant_a.id)
        db_session.add(rol)
        await db_session.flush()
        asign = Asignacion(
            tenant_id=tenant_a.id, usuario_id=user.id, rol_id=rol.id,
            materia_id=materia.id, desde=date(2026, 1, 1),
        )
        db_session.add(asign)
        await db_session.commit()

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor_seguimiento(user_id=user.id, min_aprobadas=2)

        assert result.total == 1
        assert result.estudiantes[0].nombre == "Luis"

    async def test_seguimiento_filtra_por_actividad(self, db_session, tenant_a):
        entrada, materia, version, user = await _semilla_monitor(db_session, tenant_a)
        entrada2 = await _agregar_entrada_mon(db_session, tenant_a, version, "Ana", "Diaz")

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)
        await _agregar_cal_mon(db_session, tenant_a, entrada2, materia, "TP2", nota_numerica=70)

        rol = Rol(nombre="PROF_ACT", descripcion="Prof Act", tenant_id=tenant_a.id)
        db_session.add(rol)
        await db_session.flush()
        asign = Asignacion(
            tenant_id=tenant_a.id, usuario_id=user.id, rol_id=rol.id,
            materia_id=materia.id, desde=date(2026, 1, 1),
        )
        db_session.add(asign)
        await db_session.commit()

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor_seguimiento(user_id=user.id, actividad="TP1")

        assert result.total == 2

    async def test_seguimiento_tenant_isolation(self, db_session, tenant_a, tenant_b):
        entrada_a, materia_a, _, user_a = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada_a, materia_a, "TP1", nota_numerica=80)

        rol = Rol(nombre="PROF_ISO", descripcion="Prof Iso", tenant_id=tenant_a.id)
        db_session.add(rol)
        await db_session.flush()
        asign = Asignacion(
            tenant_id=tenant_a.id, usuario_id=user_a.id, rol_id=rol.id,
            materia_id=materia_a.id, desde=date(2026, 1, 1),
        )
        db_session.add(asign)
        await db_session.commit()

        svc_b = MonitorService(db_session, tenant_b.id)
        result_b = await svc_b.get_monitor_seguimiento(user_id=user_a.id)

        assert result_b.total == 0


@pytest.mark.needs_db
class TestMonitorAdmin:
    async def test_admin_con_rango_fechas(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)

        fecha_antigua = datetime(2026, 3, 1, tzinfo=timezone.utc)
        fecha_nueva = datetime(2026, 4, 1, tzinfo=timezone.utc)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80, importado_at=fecha_antigua)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=90, importado_at=fecha_nueva)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor_admin(
            materia_id=materia.id,
            fecha_desde=date(2026, 4, 1),
            fecha_hasta=date(2026, 4, 30),
        )

        assert result.total == 1
        assert result.estudiantes[0].total_actividades == 2
        assert result.estudiantes[0].aprobadas == 1

    async def test_admin_sin_rango_igual_monitor(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=80)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_monitor_admin(materia_id=materia.id)

        assert result.total == 1
        assert result.rango_fechas is None

    async def test_admin_tenant_isolation(self, db_session, tenant_a, tenant_b):
        entrada_a, materia_a, _, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada_a, materia_a, "TP1", nota_numerica=80)

        svc_b = MonitorService(db_session, tenant_b.id)
        result_b = await svc_b.get_monitor_admin(materia_id=materia_a.id)

        assert result_b.total == 0


@pytest.mark.needs_db
class TestNotasFinales:
    async def test_notas_finales_con_mixtas(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=70)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=80)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP3", nota_textual="Satisfactorio")

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_notas_finales(materia.id)

        assert len(result.notas) == 1
        assert result.notas[0].nota_final == 75.0
        assert result.notas[0].aprobado_final is True
        assert len(result.notas[0].calificaciones) == 3

    async def test_notas_finales_solo_textuales(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_textual="Satisfactorio")
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_textual="Supera lo esperado")

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_notas_finales(materia.id)

        assert result.notas[0].nota_final is None
        assert result.notas[0].aprobado_final is True

    async def test_notas_finales_textual_no_aprobado(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_textual="Satisfactorio")
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_textual="Regular")

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_notas_finales(materia.id)

        assert result.notas[0].aprobado_final is False

    async def test_notas_finales_bajo_umbral(self, db_session, tenant_a):
        entrada, materia, _, _ = await _semilla_monitor(db_session, tenant_a)

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_numerica=50)
        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP2", nota_numerica=55)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_notas_finales(materia.id)

        assert result.notas[0].nota_final == 52.5
        assert result.notas[0].aprobado_final is False

    async def test_notas_finales_sin_calificaciones(self, db_session, tenant_a):
        _, materia, _, _ = await _semilla_monitor(db_session, tenant_a)

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_notas_finales(materia.id)

        assert result.notas == []
        assert result.status_info is not None


@pytest.mark.needs_db
class TestSinCorregir:
    async def test_sin_corregir_con_preview_token(self, db_session, tenant_a):
        entrada, materia, version, _ = await _semilla_monitor(db_session, tenant_a)

        preview_data = {
            "filename": "finalizacion.csv",
            "rows": [
                {"Nombre": "Luis", "Apellidos": "Paz", "TP1": "Completo", "TP2": "Completo"},
            ],
            "materia_id": str(materia.id),
            "_created_at": datetime.now(timezone.utc),
            "columns": [
                {"name": "Nombre", "tipo": "textual", "aprobatorio": False, "actividad": "Nombre"},
                {"name": "Apellidos", "tipo": "textual", "aprobatorio": False, "actividad": "Apellidos"},
                {"name": "TP1", "tipo": "textual", "aprobatorio": False, "actividad": "TP1"},
                {"name": "TP2", "tipo": "textual", "aprobatorio": False, "actividad": "TP2"},
            ],
        }
        token = "test-token-sin-corregir"
        CalificacionesService._preview_cache[token] = preview_data

        await _agregar_cal_mon(db_session, tenant_a, entrada, materia, "TP1", nota_textual="Satisfactorio")

        svc = MonitorService(db_session, tenant_a.id)
        result = await svc.get_sin_corregir(materia.id, token)

        assert result.total_sin_corregir == 1
        assert result.entregas[0].actividad == "TP2"

    async def test_sin_corregir_token_invalido(self, db_session, tenant_a):
        _, materia, _, _ = await _semilla_monitor(db_session, tenant_a)

        svc = MonitorService(db_session, tenant_a.id)
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await svc.get_sin_corregir(materia.id, "token-inexistente")

        assert exc_info.value.status_code == 404
