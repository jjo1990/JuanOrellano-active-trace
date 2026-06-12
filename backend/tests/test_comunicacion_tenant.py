"""Tests de tenant isolation para Comunicacion (C-12)."""

import uuid
from datetime import date

import pytest

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.user import User
from app.core.security import hash_password
from app.repositories.comunicacion_repository import ComunicacionRepository


async def _seed_tenant_data(db_session, tenant, email_prefix="t"):
    carrera = Carrera(codigo=f"{email_prefix}-C", nombre="TenantTest", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo=f"{email_prefix}-M", nombre="TenantMateria", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre=f"2026-{email_prefix}", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email=f"{email_prefix}@test.com", password_hash=hash_password("pass123!"),
        nombre="Tenant", apellidos="User", tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(user)
    return materia, user


@pytest.mark.needs_db
class TestComunicacionTenantIsolation:
    async def test_get_pendientes_tenant_a_no_ve_tenant_b(self, db_session, tenant_a, tenant_b):
        materia_a, user_a = await _seed_tenant_data(db_session, tenant_a, "a")
        materia_b, user_b = await _seed_tenant_data(db_session, tenant_b, "b")

        repo_a = ComunicacionRepository(db_session, tenant_a.id)
        repo_b = ComunicacionRepository(db_session, tenant_b.id)

        com_a = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user_a.id,
            materia_id=materia_a.id,
            destinatario="a@test.com",
            asunto="A",
            cuerpo="A",
            estado="Pendiente",
        )
        await repo_a.create(com_a)

        com_b = Comunicacion(
            tenant_id=tenant_b.id,
            enviado_por=user_b.id,
            materia_id=materia_b.id,
            destinatario="b@test.com",
            asunto="B",
            cuerpo="B",
            estado="Pendiente",
        )
        await repo_b.create(com_b)
        await db_session.commit()

        pendientes_a = await repo_a.get_pendientes(limit=10)
        assert len(pendientes_a) == 1
        assert pendientes_a[0].destinatario == "a@test.com"

        pendientes_b = await repo_b.get_pendientes(limit=10)
        assert len(pendientes_b) == 1
        assert pendientes_b[0].destinatario == "b@test.com"

    async def test_get_by_materia_cross_tenant_vacio(self, db_session, tenant_a, tenant_b):
        materia_a, user_a = await _seed_tenant_data(db_session, tenant_a, "a")
        materia_b, user_b = await _seed_tenant_data(db_session, tenant_b, "b")

        repo_a = ComunicacionRepository(db_session, tenant_a.id)

        com_b = Comunicacion(
            tenant_id=tenant_b.id,
            enviado_por=user_b.id,
            materia_id=materia_b.id,
            destinatario="b@test.com",
            asunto="B",
            cuerpo="B",
            estado="Pendiente",
        )
        db_session.add(com_b)
        await db_session.commit()

        resultados_a = await repo_a.get_by_materia(materia_b.id)
        assert len(resultados_a) == 0

    async def test_get_by_lote_cross_tenant_vacio(self, db_session, tenant_a, tenant_b):
        materia_b, user_b = await _seed_tenant_data(db_session, tenant_b, "b")
        repo_a = ComunicacionRepository(db_session, tenant_a.id)
        repo_b = ComunicacionRepository(db_session, tenant_b.id)

        lote_id = uuid.uuid4()
        com_b = Comunicacion(
            tenant_id=tenant_b.id,
            enviado_por=user_b.id,
            materia_id=materia_b.id,
            destinatario="b@test.com",
            asunto="B",
            cuerpo="B",
            estado="Pendiente",
            lote_id=lote_id,
        )
        await repo_b.create(com_b)
        await db_session.commit()

        resultados_a = await repo_a.get_by_lote(lote_id)
        assert len(resultados_a) == 0

    async def test_soft_delete_excluye_de_consultas(self, db_session, tenant_a):
        materia, user = await _seed_tenant_data(db_session, tenant_a, "a")
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        com = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="soft@test.com",
            asunto="Soft",
            cuerpo="C",
            estado="Pendiente",
            lote_id=lote_id,
        )
        created = await repo.create(com)
        await db_session.commit()

        await repo.soft_delete(created.id)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 0

        lote_result = await repo.get_by_lote(lote_id)
        assert len(lote_result) == 0

        materia_result = await repo.get_by_materia(materia.id)
        assert len(materia_result) == 0
