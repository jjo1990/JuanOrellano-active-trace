"""Tests para AvisoService (C-15) — RN-18, RN-19, RN-20."""

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.aviso import Aviso
from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.schemas.aviso import AvisoCreateRequest, AvisoUpdateRequest
from app.services.aviso_service import AvisoService


@pytest.fixture
async def seed_aviso_service(tenant_a, db_session: AsyncSession):
    tenant_id = tenant_a.id
    ahora = datetime.now(timezone.utc)

    profe_rol = Rol(nombre="PROFESOR_AVS", descripcion="Profesor", tenant_id=tenant_id)
    alumno_rol = Rol(nombre="ALUMNO_AVS", descripcion="Alumno", tenant_id=tenant_id)
    tutor_rol = Rol(nombre="TUTOR_AVS", descripcion="Tutor", tenant_id=tenant_id)
    db_session.add_all([profe_rol, alumno_rol, tutor_rol])
    await db_session.flush()

    materia_a = Materia(codigo="MAT_A", nombre="Matemática A", activa=True, tenant_id=tenant_id)
    materia_b = Materia(codigo="MAT_B", nombre="Física B", activa=True, tenant_id=tenant_id)
    db_session.add_all([materia_a, materia_b])
    await db_session.flush()

    carrera = Carrera(codigo="CAR_SRV", nombre="Ingeniería", activa=True, tenant_id=tenant_id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte_1 = Cohorte(
        carrera_id=carrera.id, nombre="2026-A", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_id,
    )
    cohorte_2 = Cohorte(
        carrera_id=carrera.id, nombre="2026-B", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_id,
    )
    db_session.add_all([cohorte_1, cohorte_2])
    await db_session.flush()

    profe_user = User(
        email="profe_avs@test.com", password_hash="hash",
        nombre="Profesor", apellidos="Avisos", tenant_id=tenant_id,
    )
    alumno_user = User(
        email="alumno_avs@test.com", password_hash="hash",
        nombre="Alumno", apellidos="Avisos", tenant_id=tenant_id,
    )
    tutor_user = User(
        email="tutor_avs@test.com", password_hash="hash",
        nombre="Tutor", apellidos="Avisos", tenant_id=tenant_id,
    )
    db_session.add_all([profe_user, alumno_user, tutor_user])
    await db_session.flush()

    asig_profe = Asignacion(
        usuario_id=profe_user.id, rol_id=profe_rol.id,
        materia_id=materia_a.id, carrera_id=carrera.id, cohorte_id=cohorte_1.id,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=None,
        tenant_id=tenant_id,
    )
    asig_alumno = Asignacion(
        usuario_id=alumno_user.id, rol_id=alumno_rol.id,
        materia_id=materia_a.id, carrera_id=carrera.id, cohorte_id=cohorte_1.id,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=None,
        tenant_id=tenant_id,
    )
    asig_tutor = Asignacion(
        usuario_id=tutor_user.id, rol_id=tutor_rol.id,
        materia_id=materia_b.id, carrera_id=carrera.id, cohorte_id=cohorte_2.id,
        comisiones=["B"], desde=date(2026, 1, 1), hasta=None,
        tenant_id=tenant_id,
    )
    db_session.add_all([asig_profe, asig_alumno, asig_tutor])
    await db_session.commit()

    return {
        "tenant_id": tenant_id,
        "profe_user_id": profe_user.id,
        "alumno_user_id": alumno_user.id,
        "tutor_user_id": tutor_user.id,
        "profe_rol_id": profe_rol.id,
        "alumno_rol_id": alumno_rol.id,
        "tutor_rol_id": tutor_rol.id,
        "materia_a_id": materia_a.id,
        "materia_b_id": materia_b.id,
        "carrera_id": carrera.id,
        "cohorte_1_id": cohorte_1.id,
        "cohorte_2_id": cohorte_2.id,
    }


@pytest.mark.needs_db
class TestAvisoServiceCrear:
    async def test_create_aviso_global_with_ack(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)

        data = AvisoCreateRequest(
            alcance="Global",
            severidad="Critico",
            titulo="Aviso Global",
            cuerpo="Cuerpo del aviso",
            inicio_en=ahora,
            fin_en=ahora + timedelta(days=7),
            requiere_ack=True,
        )

        aviso = await svc.crear_aviso(data, seed_aviso_service["tenant_id"])
        assert aviso.id is not None
        assert aviso.alcance == "Global"
        assert aviso.severidad == "Critico"
        assert aviso.requiere_ack is True
        assert aviso.activo is True

    async def test_create_aviso_by_materia(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)

        data = AvisoCreateRequest(
            alcance="PorMateria",
            materia_id=seed_aviso_service["materia_a_id"],
            rol_destino="PROFESOR",
            titulo="Aviso por Materia",
            cuerpo="Solo para profes",
            inicio_en=ahora,
            fin_en=ahora + timedelta(days=10),
        )

        aviso = await svc.crear_aviso(data, seed_aviso_service["tenant_id"])
        assert aviso.materia_id == seed_aviso_service["materia_a_id"]
        assert aviso.rol_destino == "PROFESOR"


@pytest.mark.needs_db
class TestAvisoServiceListar:
    async def test_list_avisos_with_counters(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)

        data1 = AvisoCreateRequest(
            alcance="Global", titulo="Uno", cuerpo="C1",
            inicio_en=ahora, fin_en=ahora + timedelta(days=1),
        )
        data2 = AvisoCreateRequest(
            alcance="Global", titulo="Dos", cuerpo="C2",
            inicio_en=ahora, fin_en=ahora + timedelta(days=1),
        )
        await svc.crear_aviso(data1, seed_aviso_service["tenant_id"])
        await svc.crear_aviso(data2, seed_aviso_service["tenant_id"])

        avisos = await svc.list_avisos(seed_aviso_service["tenant_id"])
        assert len(avisos) >= 2
        for a in avisos:
            assert hasattr(a, "total_vistas")
            assert hasattr(a, "total_acks")

    async def test_edit_desactivar(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)

        data = AvisoCreateRequest(
            alcance="Global", titulo="Activo", cuerpo="C",
            inicio_en=ahora, fin_en=ahora + timedelta(days=1),
        )
        created = await svc.crear_aviso(data, seed_aviso_service["tenant_id"])

        update = AvisoUpdateRequest(activo=False)
        updated = await svc.editar_aviso(
            created.id, update, seed_aviso_service["tenant_id"]
        )
        assert updated.activo is False


@pytest.mark.needs_db
class TestAvisoServiceVisibles:
    async def test_profesor_ve_avisos_de_su_materia(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        aviso_global = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Global", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )
        aviso_materia = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="PorMateria",
                materia_id=seed_aviso_service["materia_a_id"],
                titulo="Materia A", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )
        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="PorMateria",
                materia_id=seed_aviso_service["materia_b_id"],
                titulo="Materia B", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )

        visibles = await svc.list_visibles(t_id, seed_aviso_service["profe_user_id"])
        titulos = {v.titulo for v in visibles}
        assert "Global" in titulos
        assert "Materia A" in titulos
        assert "Materia B" not in titulos

    async def test_aviso_fuera_de_ventana_no_aparece(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Vencido", cuerpo="C",
                inicio_en=ahora - timedelta(days=30),
                fin_en=ahora - timedelta(days=1),
            ),
            t_id,
        )

        visibles = await svc.list_visibles(t_id, seed_aviso_service["profe_user_id"])
        titulos = {v.titulo for v in visibles}
        assert "Vencido" not in titulos

    async def test_aviso_inactivo_no_se_muestra(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        creado = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Inactivo", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )
        await svc.editar_aviso(creado.id, AvisoUpdateRequest(activo=False), t_id)

        visibles = await svc.list_visibles(t_id, seed_aviso_service["profe_user_id"])
        titulos = {v.titulo for v in visibles}
        assert "Inactivo" not in titulos

    async def test_alumno_ve_avisos_globales_y_por_rol(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Para todos", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )
        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="PorRol", rol_destino="ALUMNO_AVS",
                titulo="Solo alumnos", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )
        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="PorRol", rol_destino="PROFESOR_AVS",
                titulo="Solo profes", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )

        visibles = await svc.list_visibles(t_id, seed_aviso_service["alumno_user_id"])
        titulos = {v.titulo for v in visibles}
        assert "Para todos" in titulos
        assert "Solo alumnos" in titulos
        assert "Solo profes" not in titulos

    async def test_avisos_ordenados_por_prioridad(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Baja", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
                orden=10,
            ),
            t_id,
        )
        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Alta", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
                orden=1,
            ),
            t_id,
        )
        await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Media", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
                orden=5,
            ),
            t_id,
        )

        visibles = await svc.list_visibles(t_id, seed_aviso_service["profe_user_id"])
        titulos = [v.titulo for v in visibles]
        global_titulos = [t for t in titulos if t in ("Alta", "Media", "Baja")]
        assert global_titulos == ["Alta", "Media", "Baja"]


@pytest.mark.needs_db
class TestAvisoServiceAcknowledge:
    async def test_acknowledge_exitoso(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        aviso = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Requiere ack", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
                requiere_ack=True,
            ),
            t_id,
        )

        await svc.acknowledge(aviso.id, t_id, seed_aviso_service["profe_user_id"])

        avisos = await svc.list_avisos(t_id)
        con_ack = [a for a in avisos if a.id == aviso.id][0]
        assert con_ack.total_acks >= 1

    async def test_acknowledge_duplicado_idempotente(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        aviso = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Duplicado", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
                requiere_ack=True,
            ),
            t_id,
        )

        await svc.acknowledge(aviso.id, t_id, seed_aviso_service["profe_user_id"])
        await svc.acknowledge(aviso.id, t_id, seed_aviso_service["profe_user_id"])

        avisos = await svc.list_avisos(t_id)
        con_ack = [a for a in avisos if a.id == aviso.id][0]
        assert con_ack.total_acks == 1

    async def test_no_ack_para_aviso_sin_requiere_ack(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        aviso = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="Sin ack", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
                requiere_ack=False,
            ),
            t_id,
        )

        await svc.acknowledge(aviso.id, t_id, seed_aviso_service["profe_user_id"])

        avisos = await svc.list_avisos(t_id)
        con_ack = [a for a in avisos if a.id == aviso.id][0]
        assert con_ack.total_acks == 0


@pytest.mark.needs_db
class TestAvisoServiceSoftDelete:
    async def test_soft_delete_oculta_aviso(self, seed_aviso_service, db_session):
        svc = AvisoService(db_session, seed_aviso_service["tenant_id"])
        ahora = datetime.now(timezone.utc)
        t_id = seed_aviso_service["tenant_id"]

        aviso = await svc.crear_aviso(
            AvisoCreateRequest(
                alcance="Global", titulo="ABorrar", cuerpo="C",
                inicio_en=ahora, fin_en=ahora + timedelta(days=1),
            ),
            t_id,
        )

        await svc.eliminar_aviso(aviso.id, t_id)

        visibles = await svc.list_visibles(t_id, seed_aviso_service["profe_user_id"])
        titulos = {v.titulo for v in visibles}
        assert "ABorrar" not in titulos
