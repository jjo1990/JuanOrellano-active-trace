import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.schemas.equipo import (
    AsignacionMasivaRequest,
    BuscarUsuariosParams,
    ClonarEquipoRequest,
    ExportarEquipoParams,
    MisEquiposFilterParams,
    ModificarVigenciaRequest,
    UsuarioBulkItem,
)
from app.services.equipo_service import EquipoService


@pytest.fixture
async def seed_equipo_service(db_session, tenant_a):
    profe_rol = Rol(nombre="PROFESOR_SVC", descripcion="Prof Svc", tenant_id=tenant_a.id)
    tutor_rol = Rol(nombre="TUTOR_SVC", descripcion="Tutor Svc", tenant_id=tenant_a.id)
    db_session.add_all([profe_rol, tutor_rol])
    await db_session.flush()

    materia = Materia(codigo="MAT_SVC", nombre="Matematica Svc", activa=True, tenant_id=tenant_a.id)
    materia2 = Materia(codigo="FIS_SVC", nombre="Fisica Svc", activa=True, tenant_id=tenant_a.id)
    db_session.add_all([materia, materia2])
    await db_session.flush()

    carrera = Carrera(codigo="CAR_SVC", nombre="Ingenieria Svc", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte_orig = Cohorte(
        carrera_id=carrera.id, nombre="2026-A", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    cohorte_dest = Cohorte(
        carrera_id=carrera.id, nombre="2026-B", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add_all([cohorte_orig, cohorte_dest])
    await db_session.flush()

    user1 = User(email="svc1@test.com", password_hash="hash",
                 nombre="Juan", apellidos="Perez", legajo="L-001", tenant_id=tenant_a.id)
    user2 = User(email="svc2@test.com", password_hash="hash",
                 nombre="Maria", apellidos="Gomez", legajo="L-002", tenant_id=tenant_a.id)
    user3 = User(email="svc3@test.com", password_hash="hash",
                 nombre="Carlos", apellidos="Lopez", legajo="L-003", tenant_id=tenant_a.id)
    db_session.add_all([user1, user2, user3])
    await db_session.flush()

    asig1 = Asignacion(
        usuario_id=user1.id, rol_id=profe_rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_orig.id,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    asig2 = Asignacion(
        usuario_id=user2.id, rol_id=tutor_rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_orig.id,
        comisiones=["B"], desde=date(2026, 1, 1), hasta=None,
        tenant_id=tenant_a.id,
    )
    asig_deleted = Asignacion(
        usuario_id=user3.id, rol_id=profe_rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte_orig.id,
        comisiones=["C"], desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
        tenant_id=tenant_a.id, deleted_at=datetime.now(timezone.utc),
    )
    db_session.add_all([asig1, asig2, asig_deleted])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user1_id": user1.id,
        "user2_id": user2.id,
        "user3_id": user3.id,
        "profe_rol_id": profe_rol.id,
        "tutor_rol_id": tutor_rol.id,
        "materia_id": materia.id,
        "materia2_id": materia2.id,
        "carrera_id": carrera.id,
        "cohorte_orig_id": cohorte_orig.id,
        "cohorte_dest_id": cohorte_dest.id,
        "asig1_id": asig1.id,
        "asig2_id": asig2.id,
        "asig_deleted_id": asig_deleted.id,
    }


@pytest.mark.needs_db
class TestGetMisEquipos:
    async def test_returns_enriched_data(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])
        results = await svc.get_mis_equipos(d["user1_id"], MisEquiposFilterParams())

        assert len(results) >= 1
        r = results[0]
        assert r.usuario_nombre == "Juan"
        assert r.usuario_apellidos == "Perez"
        assert r.usuario_email == "svc1@test.com"
        assert r.rol_nombre == "PROFESOR_SVC"
        assert r.materia_nombre == "Matematica Svc"
        assert r.carrera_nombre == "Ingenieria Svc"
        assert r.cohorte_nombre == "2026-A"
        assert r.comisiones == ["A"]
        assert r.estado_vigencia in ("Vigente", "Vencida")

    async def test_filters_by_vigente(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])
        results = await svc.get_mis_equipos(d["user1_id"], MisEquiposFilterParams(vigente=True))
        assert len(results) >= 1

    async def test_filters_by_materia(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])
        results = await svc.get_mis_equipos(d["user2_id"], MisEquiposFilterParams(materia_id=d["materia_id"]))
        assert len(results) == 1

    async def test_combined_filters(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])
        results = await svc.get_mis_equipos(
            d["user1_id"],
            MisEquiposFilterParams(vigente=True, materia_id=d["materia_id"], rol_id=d["profe_rol_id"]),
        )
        assert len(results) >= 1

    async def test_user_without_assignments_returns_empty(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])
        fake_id = uuid.uuid4()
        results = await svc.get_mis_equipos(fake_id, MisEquiposFilterParams())
        assert len(results) == 0

    async def test_excludes_soft_deleted(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])
        results = await svc.get_mis_equipos(d["user3_id"], MisEquiposFilterParams())
        assert len(results) == 0


@pytest.mark.needs_db
class TestAsignacionMasiva:
    async def test_creates_multiple_assignments(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = AsignacionMasivaRequest(
            usuarios=[UsuarioBulkItem(id=d["user1_id"]), UsuarioBulkItem(id=d["user2_id"])],
            materia_id=d["materia2_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_orig_id"],
            rol_id=d["profe_rol_id"],
            comisiones=["A", "B"],
            desde=date(2026, 8, 1),
            hasta=date(2026, 12, 31),
        )
        resp = await svc.asignacion_masiva(req)
        await db_session.commit()

        assert resp.total_procesados == 2
        assert resp.total_exitosos == 2
        assert resp.total_fallidos == 0
        assert len(resp.asignaciones_creadas) == 2
        assert len(resp.errores) == 0

    async def test_best_effort_with_invalid_user(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        fake_id = uuid.uuid4()
        req = AsignacionMasivaRequest(
            usuarios=[UsuarioBulkItem(id=d["user1_id"]), UsuarioBulkItem(id=fake_id)],
            materia_id=d["materia2_id"],
            rol_id=d["profe_rol_id"],
            desde=date(2026, 8, 1),
        )
        resp = await svc.asignacion_masiva(req)
        await db_session.commit()

        assert resp.total_procesados == 2
        assert resp.total_exitosos == 1
        assert resp.total_fallidos == 1
        assert len(resp.errores) == 1

    async def test_all_users_invalid(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = AsignacionMasivaRequest(
            usuarios=[UsuarioBulkItem(id=uuid.uuid4()), UsuarioBulkItem(id=uuid.uuid4())],
            materia_id=d["materia2_id"],
            rol_id=d["profe_rol_id"],
            desde=date(2026, 8, 1),
        )
        resp = await svc.asignacion_masiva(req)
        await db_session.commit()

        assert resp.total_procesados == 2
        assert resp.total_exitosos == 0
        assert resp.total_fallidos == 2
        assert len(resp.asignaciones_creadas) == 0


@pytest.mark.needs_db
class TestClonarEquipo:
    async def test_clona_correctly(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ClonarEquipoRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_origen_id=d["cohorte_orig_id"],
            cohorte_destino_id=d["cohorte_dest_id"],
            desde=date(2027, 1, 1),
            hasta=date(2027, 12, 31),
        )
        resp = await svc.clonar_equipo(req)
        await db_session.commit()

        assert resp.total_clonadas == 2
        assert len(resp.asignaciones_creadas) == 2
        for a in resp.asignaciones_creadas:
            assert a["cohorte_id"] == str(d["cohorte_dest_id"])
            assert a["desde"] == "2027-01-01"
            assert a["hasta"] == "2027-12-31"

    async def test_ignores_soft_deleted(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ClonarEquipoRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_origen_id=d["cohorte_orig_id"],
            cohorte_destino_id=d["cohorte_dest_id"],
            desde=date(2027, 1, 1),
            hasta=None,
        )
        resp = await svc.clonar_equipo(req)
        await db_session.commit()

        assert resp.total_clonadas == 2

    async def test_origin_empty_returns_zero(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ClonarEquipoRequest(
            materia_id=d["materia2_id"],
            carrera_id=d["carrera_id"],
            cohorte_origen_id=d["cohorte_orig_id"],
            cohorte_destino_id=d["cohorte_dest_id"],
            desde=date(2027, 1, 1),
            hasta=None,
        )
        resp = await svc.clonar_equipo(req)
        await db_session.commit()

        assert resp.total_clonadas == 0

    async def test_origin_with_null_dates(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ClonarEquipoRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_origen_id=d["cohorte_orig_id"],
            cohorte_destino_id=d["cohorte_dest_id"],
            desde=date(2027, 1, 1),
            hasta=None,
        )
        resp = await svc.clonar_equipo(req)
        await db_session.commit()

        assert resp.total_clonadas == 2
        for a in resp.asignaciones_creadas:
            assert a["hasta"] is None


@pytest.mark.needs_db
class TestModificarVigenciaBloque:
    async def test_updates_fechas(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ModificarVigenciaRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_orig_id"],
            desde=date(2027, 1, 1),
            hasta=date(2027, 12, 31),
        )
        resp = await svc.modificar_vigencia_bloque(req)
        await db_session.commit()

        assert resp.asignaciones_actualizadas >= 2
        assert resp.total_encontradas >= 2

    async def test_no_match_returns_zero(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ModificarVigenciaRequest(
            materia_id=uuid.uuid4(),
            desde=date(2027, 1, 1),
        )
        resp = await svc.modificar_vigencia_bloque(req)
        assert resp.asignaciones_actualizadas == 0

    async def test_only_desde(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        req = ModificarVigenciaRequest(
            materia_id=d["materia_id"],
            desde=date(2027, 1, 1),
        )
        resp = await svc.modificar_vigencia_bloque(req)
        await db_session.commit()

        assert resp.asignaciones_actualizadas >= 2


@pytest.mark.needs_db
class TestExportarEquipo:
    async def test_generates_csv(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        params = ExportarEquipoParams(materia_id=d["materia_id"])
        csv_str = await svc.exportar_equipo(params)

        assert "nombre" in csv_str.lower()
        assert "apellido" in csv_str.lower()
        assert "email" in csv_str.lower()
        assert "legajo" in csv_str.lower()
        assert "rol" in csv_str.lower()
        assert "materia" in csv_str.lower()
        assert "carrera" in csv_str.lower()
        assert "cohorte" in csv_str.lower()
        assert "comisiones" in csv_str.lower()
        assert "desde" in csv_str.lower()
        assert "hasta" in csv_str.lower()
        assert "estado" in csv_str.lower()

    async def test_csv_contains_data(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        params = ExportarEquipoParams(materia_id=d["materia_id"])
        csv_str = await svc.exportar_equipo(params)

        assert "Juan" in csv_str
        assert "Perez" in csv_str
        assert "Maria" in csv_str

    async def test_csv_ignores_deleted(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        params = ExportarEquipoParams(materia_id=d["materia_id"])
        csv_str = await svc.exportar_equipo(params)

        assert "Carlos" not in csv_str

    async def test_csv_with_multiple_comisiones(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        params = ExportarEquipoParams(materia_id=d["materia_id"])
        csv_str = await svc.exportar_equipo(params)
        assert "A" in csv_str


@pytest.mark.needs_db
class TestBuscarUsuarios:
    async def test_returns_matching_users(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        params = BuscarUsuariosParams(q="mar")
        results = await svc.buscar_usuarios(params)

        assert len(results) >= 1
        assert all(hasattr(r, "id") for r in results)
        assert all(hasattr(r, "nombre") for r in results)

    async def test_empty_query_returns_empty(self, db_session, seed_equipo_service):
        d = seed_equipo_service
        svc = EquipoService(db_session, d["tenant_a_id"])

        params = BuscarUsuariosParams(q="")
        results = await svc.buscar_usuarios(params)

        assert len(results) == 0
