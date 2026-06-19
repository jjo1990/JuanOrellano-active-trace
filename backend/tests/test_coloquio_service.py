"""TDD tests for ColoquioService."""

import uuid
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException

from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.models.permiso import Permiso
from app.models.reserva_evaluacion import ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user import User
from app.models.usuario_rol import UsuarioRol
from app.schemas.coloquio import (
    AgendaFilterParams,
    EvaluacionCreateRequest,
    EvaluacionUpdateRequest,
    ImportAlumnoItem,
    ImportAlumnosRequest,
    ReservaCreateRequest,
    ResultadoCreateRequest,
    ResultadosFilterParams,
)
from app.services.coloquio_service import ColoquioService


@pytest.fixture
async def seed_coloquio_service(db_session, tenant_a):
    coord = User(
        email="coord@test.com", password_hash="hash",
        nombre="Coord", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-COORD",
    )
    db_session.add(coord)

    alumno = User(
        email="alumno@test.com", password_hash="hash",
        nombre="Alumno", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-AL",
    )
    db_session.add(alumno)

    alumno2 = User(
        email="alumno2@test.com", password_hash="hash",
        nombre="Alumno2", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-AL2",
    )
    db_session.add(alumno2)

    await db_session.flush()

    rol_coord = Rol(nombre="COORDINADOR", descripcion="Coord", tenant_id=tenant_a.id)
    db_session.add(rol_coord)

    rol_alumno = Rol(nombre="ALUMNO", descripcion="Alumno", tenant_id=tenant_a.id)
    db_session.add(rol_alumno)

    await db_session.flush()

    perm_gestionar = Permiso(
        codigo="coloquios:gestionar", descripcion="Gestionar coloquios",
        modulo="coloquios", tenant_id=tenant_a.id,
    )
    db_session.add(perm_gestionar)

    perm_reservar = Permiso(
        codigo="coloquios:reservar", descripcion="Reservar coloquios",
        modulo="coloquios", tenant_id=tenant_a.id,
    )
    db_session.add(perm_reservar)

    await db_session.flush()

    rp1 = RolPermiso(rol_id=rol_coord.id, permiso_id=perm_gestionar.id, tenant_id=tenant_a.id)
    rp2 = RolPermiso(rol_id=rol_alumno.id, permiso_id=perm_reservar.id, tenant_id=tenant_a.id)
    db_session.add_all([rp1, rp2])

    ahora = datetime.now(timezone.utc)
    ur1 = UsuarioRol(user_id=coord.id, rol_id=rol_coord.id, tenant_id=tenant_a.id, fecha_desde=ahora)
    ur2 = UsuarioRol(user_id=alumno.id, rol_id=rol_alumno.id, tenant_id=tenant_a.id, fecha_desde=ahora)
    ur3 = UsuarioRol(user_id=alumno2.id, rol_id=rol_alumno.id, tenant_id=tenant_a.id, fecha_desde=ahora)
    db_session.add_all([ur1, ur2, ur3])

    await db_session.flush()

    materia = Materia(codigo="MAT_SVC", nombre="Materia Svc", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(nombre="Carrera Svc", codigo="CAR_SVC", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="Cohorte Svc",
        anio=2026, vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "coord_id": coord.id,
        "alumno_id": alumno.id,
        "alumno2_id": alumno2.id,
        "materia_id": materia.id,
        "cohorte_id": cohorte.id,
        "rol_coord_id": rol_coord.id,
        "rol_alumno_id": rol_alumno.id,
    }


@pytest.mark.needs_db
class TestColoquioServiceCrear:
    async def test_crear_evaluacion_exitosa(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data = EvaluacionCreateRequest(
            materia_id=d["materia_id"],
            cohorte_id=d["cohorte_id"],
            tipo="Coloquio",
            instancia="Coloquio Final",
            dias_disponibles=3,
            cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data, d["tenant_a_id"])
        assert ev.id is not None
        assert ev.estado == "Activa"
        assert ev.tipo == "Coloquio"
        assert ev.cupos_por_dia == 5

    async def test_crear_evaluacion_tp(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data = EvaluacionCreateRequest(
            materia_id=d["materia_id"],
            cohorte_id=d["cohorte_id"],
            tipo="TP",
            instancia="TP Integrador",
            dias_disponibles=7,
            cupos_por_dia=10,
        )
        ev = await svc.crear_evaluacion(data, d["tenant_a_id"])
        assert ev.tipo == "TP"


@pytest.mark.needs_db
class TestColoquioServiceEditar:
    async def test_cerrar_evaluacion(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=1, cupos_por_dia=2,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        data_u = EvaluacionUpdateRequest(estado="Cerrada")
        ev_updated = await svc.editar_evaluacion(ev.id, data_u, d["tenant_a_id"])
        assert ev_updated.estado == "Cerrada"

    async def test_modificar_cupos(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Parcial", instancia="Test", dias_disponibles=1, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        data_u = EvaluacionUpdateRequest(cupos_por_dia=10)
        ev_updated = await svc.editar_evaluacion(ev.id, data_u, d["tenant_a_id"])
        assert ev_updated.cupos_por_dia == 10


@pytest.mark.needs_db
class TestColoquioServiceImportar:
    async def test_importar_alumnos(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=1, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        importados = await svc.importar_alumnos(
            ev.id,
            ImportAlumnosRequest(alumnos=[
                ImportAlumnoItem(user_id=d["alumno_id"]),
                ImportAlumnoItem(user_id=d["alumno2_id"]),
            ]),
            d["tenant_a_id"],
        )
        assert importados == 2

    async def test_importar_alumno_duplicado_idempotente(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=1, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        importados1 = await svc.importar_alumnos(
            ev.id,
            ImportAlumnosRequest(alumnos=[ImportAlumnoItem(user_id=d["alumno_id"])]),
            d["tenant_a_id"],
        )
        assert importados1 == 1

        importados2 = await svc.importar_alumnos(
            ev.id,
            ImportAlumnosRequest(alumnos=[ImportAlumnoItem(user_id=d["alumno_id"])]),
            d["tenant_a_id"],
        )
        assert importados2 == 0


@pytest.mark.needs_db
class TestColoquioServiceReservar:
    async def test_reservar_turno_con_cupo(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        fecha = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        data_r = ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha)
        reserva = await svc.reservar_turno(data_r, d["tenant_a_id"], d["alumno_id"])
        assert reserva.estado == "Activa"
        assert reserva.alumno_id == d["alumno_id"]

    async def test_reservar_sin_cupo_409(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=1,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        fecha = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        await svc.reservar_turno(
            ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha),
            d["tenant_a_id"], d["alumno_id"],
        )
        await db_session.commit()

        with pytest.raises(HTTPException) as exc:
            await svc.reservar_turno(
                ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha),
                d["tenant_a_id"], d["alumno2_id"],
            )
        assert exc.value.status_code == 409
        assert "Cupo agotado" in exc.value.detail

    async def test_reservar_convocatoria_cerrada_422(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await svc.editar_evaluacion(ev.id, EvaluacionUpdateRequest(estado="Cerrada"), d["tenant_a_id"])
        await db_session.commit()

        fecha = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        with pytest.raises(HTTPException) as exc:
            await svc.reservar_turno(
                ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha),
                d["tenant_a_id"], d["alumno_id"],
            )
        assert exc.value.status_code == 422
        assert "cerrada" in exc.value.detail.lower()

    async def test_reservar_duplicado_409(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        fecha1 = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        await svc.reservar_turno(
            ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha1),
            d["tenant_a_id"], d["alumno_id"],
        )
        await db_session.commit()

        fecha2 = datetime(2026, 7, 2, 14, 0, tzinfo=timezone.utc)
        with pytest.raises(HTTPException) as exc:
            await svc.reservar_turno(
                ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha2),
                d["tenant_a_id"], d["alumno_id"],
            )
        assert exc.value.status_code == 409
        assert "reserva activa" in exc.value.detail.lower()


@pytest.mark.needs_db
class TestColoquioServiceCancelar:
    async def test_alumno_cancela_reserva_propia(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        fecha = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        reserva = await svc.reservar_turno(
            ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha),
            d["tenant_a_id"], d["alumno_id"],
        )
        await db_session.commit()

        await svc.cancelar_reserva(reserva.id, d["tenant_a_id"], d["alumno_id"], is_coordinador=False)
        await db_session.commit()

        from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        r = await repo.get_by_id(reserva.id, d["tenant_a_id"])
        assert r.estado == "Cancelada"

    async def test_alumno_cancela_reserva_ajena_403(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        fecha = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        reserva = await svc.reservar_turno(
            ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha),
            d["tenant_a_id"], d["alumno_id"],
        )
        await db_session.commit()

        with pytest.raises(HTTPException) as exc:
            await svc.cancelar_reserva(
                reserva.id, d["tenant_a_id"], d["alumno2_id"], is_coordinador=False,
            )
        assert exc.value.status_code == 403

    async def test_coordinador_cancela_reserva(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=3, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        fecha = datetime(2026, 7, 1, 14, 0, tzinfo=timezone.utc)
        reserva = await svc.reservar_turno(
            ReservaCreateRequest(evaluacion_id=ev.id, fecha_hora=fecha),
            d["tenant_a_id"], d["alumno_id"],
        )
        await db_session.commit()

        await svc.cancelar_reserva(reserva.id, d["tenant_a_id"], d["coord_id"], is_coordinador=True)
        await db_session.commit()

        from app.repositories.reserva_evaluacion_repository import ReservaEvaluacionRepository
        repo = ReservaEvaluacionRepository(db_session, d["tenant_a_id"])
        r = await repo.get_by_id(reserva.id, d["tenant_a_id"])
        assert r.estado == "Cancelada"


@pytest.mark.needs_db
class TestColoquioServiceResultado:
    async def test_registrar_nota_alumno_importado(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=1, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        await svc.importar_alumnos(
            ev.id,
            ImportAlumnosRequest(alumnos=[ImportAlumnoItem(user_id=d["alumno_id"])]),
            d["tenant_a_id"],
        )
        await db_session.commit()

        resultado = await svc.registrar_resultado(
            ResultadoCreateRequest(
                evaluacion_id=ev.id, alumno_id=d["alumno_id"], nota_final="8",
            ),
            d["tenant_a_id"],
        )
        assert resultado.nota_final == "8"

    async def test_registrar_nota_alumno_no_importado_404(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=1, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        with pytest.raises(HTTPException) as exc:
            await svc.registrar_resultado(
                ResultadoCreateRequest(
                    evaluacion_id=ev.id, alumno_id=d["alumno_id"], nota_final="8",
                ),
                d["tenant_a_id"],
            )
        assert exc.value.status_code == 404
        assert "no está" in exc.value.detail.lower()


@pytest.mark.needs_db
class TestColoquioServiceMetricas:
    async def test_metricas_con_datos(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        data_c = EvaluacionCreateRequest(
            materia_id=d["materia_id"], cohorte_id=d["cohorte_id"],
            tipo="Coloquio", instancia="Test", dias_disponibles=1, cupos_por_dia=5,
        )
        ev = await svc.crear_evaluacion(data_c, d["tenant_a_id"])
        await db_session.commit()

        await svc.importar_alumnos(
            ev.id,
            ImportAlumnosRequest(alumnos=[ImportAlumnoItem(user_id=d["alumno_id"])]),
            d["tenant_a_id"],
        )
        await db_session.commit()

        metricas = await svc.get_metricas(d["tenant_a_id"])
        assert metricas.total_alumnos_cargados == 1
        assert metricas.total_instancias_activas == 1
        assert metricas.total_notas_registradas == 0

    async def test_metricas_sin_datos(self, db_session, seed_coloquio_service):
        d = seed_coloquio_service
        svc = ColoquioService(db_session, d["tenant_a_id"])
        metricas = await svc.get_metricas(d["tenant_a_id"])
        assert metricas.total_alumnos_cargados == 0
        assert metricas.total_instancias_activas == 0
        assert metricas.total_reservas_activas == 0
        assert metricas.total_notas_registradas == 0
