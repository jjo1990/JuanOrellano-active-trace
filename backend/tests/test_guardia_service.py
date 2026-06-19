"""TDD tests for GuardiaService."""

import uuid
from datetime import date

import pytest

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.guardia import Guardia
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.schemas.guardia import GuardiaCreateRequest, GuardiaUpdateRequest
from app.services.guardia_service import GuardiaService


@pytest.fixture
async def seed_guardia_svc(db_session, tenant_a):
    user1 = User(
        email="svc_tutor@test.com", password_hash="hash",
        nombre="Tutor", apellidos="Uno", tenant_id=tenant_a.id,
        legajo="L-030",
    )
    user2 = User(
        email="svc_tutor2@test.com", password_hash="hash",
        nombre="Tutor", apellidos="Dos", tenant_id=tenant_a.id,
        legajo="L-031",
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    rol = Rol(nombre="TUTOR_SVC", descripcion="Tutor Service", tenant_id=tenant_a.id)
    db_session.add(rol)
    await db_session.flush()

    materia = Materia(codigo="MAT_GSVC", nombre="Materia GSvc", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(codigo="CAR_GSVC", nombre="Carrera GSvc", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="COH_GSVC", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    asig1 = Asignacion(
        usuario_id=user1.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    asig2 = Asignacion(
        usuario_id=user2.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        comisiones=["B"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    db_session.add_all([asig1, asig2])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user1_id": user1.id,
        "user2_id": user2.id,
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "asig1_id": asig1.id,
        "asig2_id": asig2.id,
    }


@pytest.mark.needs_db
class TestGuardiaService:
    async def test_registrar_guardia_exitosa(self, db_session, seed_guardia_svc):
        d = seed_guardia_svc
        svc = GuardiaService(db_session, d["tenant_a_id"])

        data = GuardiaCreateRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            asignacion_id=d["asig1_id"],
            dia="Lunes",
            horario="14:00–14:45",
            estado="Realizada",
            comentarios="Todo OK",
        )
        guardia = await svc.registrar(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        assert guardia is not None
        assert guardia.estado == "Realizada"
        assert guardia.dia == "Lunes"

    async def test_editar_guardia_propia(self, db_session, seed_guardia_svc):
        d = seed_guardia_svc
        svc = GuardiaService(db_session, d["tenant_a_id"])

        data = GuardiaCreateRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            asignacion_id=d["asig1_id"],
            dia="Martes",
            horario="15:00–15:45",
            estado="Pendiente",
        )
        guardia = await svc.registrar(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        update_data = GuardiaUpdateRequest(
            estado="Cancelada",
            comentarios="Alumno no se presento",
        )
        updated = await svc.editar(guardia.id, update_data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        assert updated.estado == "Cancelada"
        assert updated.comentarios == "Alumno no se presento"

    async def test_listar_guardias_con_filtros(self, db_session, seed_guardia_svc):
        d = seed_guardia_svc
        svc = GuardiaService(db_session, d["tenant_a_id"])

        data1 = GuardiaCreateRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            asignacion_id=d["asig1_id"],
            dia="Lunes", horario="10:00–10:45", estado="Realizada",
        )
        data2 = GuardiaCreateRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            asignacion_id=d["asig1_id"],
            dia="Martes", horario="11:00–11:45", estado="Pendiente",
        )
        await svc.registrar(data1, d["tenant_a_id"], d["user1_id"])
        await svc.registrar(data2, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        results = await svc.listar(d["tenant_a_id"], d["user1_id"], estado="Realizada")
        assert len(results) == 1
        assert results[0].estado == "Realizada"

    async def test_exportar_csv_con_datos(self, db_session, seed_guardia_svc):
        d = seed_guardia_svc
        svc = GuardiaService(db_session, d["tenant_a_id"])

        data = GuardiaCreateRequest(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            asignacion_id=d["asig1_id"],
            dia="Lunes", horario="10:00–10:45", estado="Realizada",
        )
        await svc.registrar(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        csv_content = await svc.exportar_csv(d["tenant_a_id"], d["user1_id"])
        assert "Materia" in csv_content
        assert "Carrera" in csv_content
        assert "Lunes" in csv_content

    async def test_exportar_csv_sin_datos_devuelve_headers(self, db_session, seed_guardia_svc):
        d = seed_guardia_svc
        svc = GuardiaService(db_session, d["tenant_a_id"])

        csv_content = await svc.exportar_csv(d["tenant_a_id"], d["user1_id"])
        assert "Materia" in csv_content
        assert "Carrera" in csv_content
        lines = csv_content.strip().split("\n")
        assert len(lines) == 1
