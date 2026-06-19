"""TDD tests for EncuentroService."""

import uuid
from datetime import date, time

import pytest

from app.models.asignacion import Asignacion
from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.slot_encuentro import SlotEncuentro
from app.models.user import User
from app.schemas.encuentro import InstanciaCreateRequest, InstanciaUpdateRequest, SlotCreateRequest
from app.services.encuentro_service import EncuentroService


@pytest.fixture
async def seed_encuentro_svc(db_session, tenant_a):
    user1 = User(
        email="svc_profe@test.com", password_hash="hash",
        nombre="Profesor", apellidos="Uno", tenant_id=tenant_a.id,
        legajo="L-020",
    )
    user2 = User(
        email="svc_profe2@test.com", password_hash="hash",
        nombre="Profesor", apellidos="Dos", tenant_id=tenant_a.id,
        legajo="L-021",
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    rol = Rol(nombre="PROFESOR_SVC", descripcion="Prof Service", tenant_id=tenant_a.id)
    db_session.add(rol)
    await db_session.flush()

    materia = Materia(codigo="MAT_SVC", nombre="Materia Service", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    asig1 = Asignacion(
        usuario_id=user1.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=None, cohorte_id=None,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    db_session.add(asig1)
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "user1_id": user1.id,
        "user2_id": user2.id,
        "materia_id": materia.id,
        "asig1_id": asig1.id,
    }


@pytest.mark.needs_db
class TestEncuentroServiceSlotCreation:
    async def test_crear_slot_recurrente_genera_instancias(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Clase Recurrente",
            hora=time(18, 0),
            dia_semana="Lunes",
            fecha_inicio=date(2026, 3, 9),
            cant_semanas=4,
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        assert slot is not None
        assert slot.cant_semanas == 4

        from sqlalchemy import select
        stmt = select(InstanciaEncuentro).where(
            InstanciaEncuentro.slot_id == slot.id,
            InstanciaEncuentro.tenant_id == d["tenant_a_id"],
            InstanciaEncuentro.deleted_at.is_(None),
        ).order_by(InstanciaEncuentro.fecha)
        result = await db_session.execute(stmt)
        instancias = result.scalars().all()
        assert len(instancias) == 4
        assert instancias[0].fecha == date(2026, 3, 9)

    async def test_crear_slot_unico_genera_una_instancia(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Clase Unica",
            hora=time(10, 0),
            fecha_unica=date(2026, 4, 15),
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        from sqlalchemy import select
        stmt = select(InstanciaEncuentro).where(
            InstanciaEncuentro.slot_id == slot.id,
            InstanciaEncuentro.deleted_at.is_(None),
        )
        result = await db_session.execute(stmt)
        instancias = result.scalars().all()
        assert len(instancias) == 1
        assert instancias[0].fecha == date(2026, 4, 15)

    async def test_crear_slot_sin_modo_espera_valueerror(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SlotCreateRequest(
                titulo="Sin modo",
                hora=time(10, 0),
                materia_id=d["materia_id"],
                asignacion_id=d["asig1_id"],
            )

    async def test_crear_slot_recurrente_con_cant_semanas_cero(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SlotCreateRequest(
                titulo="Recurrente cero",
                hora=time(10, 0),
                dia_semana="Lunes",
                fecha_inicio=date(2026, 3, 9),
                cant_semanas=0,
                materia_id=d["materia_id"],
                asignacion_id=d["asig1_id"],
            )


@pytest.mark.needs_db
class TestEncuentroServiceInstancia:
    async def test_crear_instancia_independiente(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = InstanciaCreateRequest(
            fecha=date(2026, 5, 10),
            hora=time(14, 0),
            titulo="Consulta pre-parcial",
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        inst = await svc.crear_instancia(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        assert inst is not None
        assert inst.slot_id is None
        assert inst.estado == "Programado"

    async def test_editar_instancia_no_afecta_otras(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Slot Edicion",
            hora=time(18, 0),
            dia_semana="Martes",
            fecha_inicio=date(2026, 4, 7),
            cant_semanas=2,
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        from sqlalchemy import select
        stmt = select(InstanciaEncuentro).where(
            InstanciaEncuentro.slot_id == slot.id,
            InstanciaEncuentro.deleted_at.is_(None),
        ).order_by(InstanciaEncuentro.fecha)
        result = await db_session.execute(stmt)
        instancias = result.scalars().all()
        assert len(instancias) == 2

        update_data = InstanciaUpdateRequest(
            estado="Realizado",
            video_url="https://meet.google.com/rec/abc",
        )
        updated = await svc.editar_instancia(instancias[0].id, update_data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        assert updated.estado == "Realizado"
        assert updated.video_url == "https://meet.google.com/rec/abc"

        other = await db_session.get(InstanciaEncuentro, instancias[1].id)
        assert other.estado == "Programado"


@pytest.mark.needs_db
class TestEncuentroServiceAulaVirtual:
    async def test_generar_html_aula_virtual_con_instancias(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Clase HTML",
            hora=time(14, 0),
            dia_semana="Viernes",
            fecha_inicio=date(2026, 5, 1),
            cant_semanas=1,
            meet_url="https://meet.google.com/xyz",
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        html = await svc.generar_html_aula_virtual(slot.id, d["tenant_a_id"])
        assert "Clase HTML" in html
        assert "https://meet.google.com/xyz" in html
        assert "Programado" in html

    async def test_generar_html_aula_virtual_sin_instancias(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        slot = SlotEncuentro(
            titulo="Slot sin instancias",
            hora=time(10, 0),
            fecha_unica=date(2026, 6, 1),
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
            tenant_id=d["tenant_a_id"],
        )
        db_session.add(slot)
        await db_session.commit()

        html = await svc.generar_html_aula_virtual(slot.id, d["tenant_a_id"])
        assert "No hay encuentros programados" in html


@pytest.mark.needs_db
class TestEncuentroServiceQueries:
    async def test_get_slot_con_instancias_slot_encontrado(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Slot Query",
            hora=time(9, 0),
            fecha_unica=date(2026, 7, 1),
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        found = await svc.get_slot_con_instancias(slot.id, d["tenant_a_id"])
        assert found is not None
        assert found.titulo == "Slot Query"

    async def test_get_slot_con_instancias_no_encontrado(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await svc.get_slot_con_instancias(uuid.uuid4(), d["tenant_a_id"])
        assert exc.value.status_code == 404

    async def test_list_mis_encuentros_con_asignaciones(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Mi Encuentro",
            hora=time(11, 0),
            fecha_unica=date(2026, 8, 1),
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        slots = await svc.list_mis_encuentros(d["tenant_a_id"], d["user1_id"])
        assert len(slots) >= 1
        assert any(s.titulo == "Mi Encuentro" for s in slots)

    async def test_list_mis_encuentros_sin_asignaciones(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        slots = await svc.list_mis_encuentros(d["tenant_a_id"], d["user2_id"])
        assert slots == []

    async def test_list_admin_con_filtros(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        data = SlotCreateRequest(
            titulo="Admin Slot",
            hora=time(15, 0),
            dia_semana="Miercoles",
            fecha_inicio=date(2026, 3, 4),
            cant_semanas=1,
            materia_id=d["materia_id"],
            asignacion_id=d["asig1_id"],
        )
        slot = await svc.crear_slot(data, d["tenant_a_id"], d["user1_id"])
        await db_session.commit()

        from app.schemas.encuentro import AdminEncuentrosFilterParams
        filtros = AdminEncuentrosFilterParams()
        slots = await svc.list_admin(d["tenant_a_id"], filtros)
        assert len(slots) >= 1

        filtros_estado = AdminEncuentrosFilterParams(estado="Programado")
        slots = await svc.list_admin(d["tenant_a_id"], filtros_estado)
        assert len(slots) >= 1

    async def test_editar_instancia_no_encontrada(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        update = InstanciaUpdateRequest(estado="Realizado")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await svc.editar_instancia(uuid.uuid4(), update, d["tenant_a_id"], d["user1_id"])
        assert exc.value.status_code == 404

    async def test_generar_html_slot_no_encontrado(self, db_session, seed_encuentro_svc):
        d = seed_encuentro_svc
        svc = EncuentroService(db_session, d["tenant_a_id"])

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await svc.generar_html_aula_virtual(uuid.uuid4(), d["tenant_a_id"])
        assert exc.value.status_code == 404
