"""Tests para dispatch_worker (C-12)."""

import uuid
from datetime import date

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.security import hash_password
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.user import User
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.workers.dispatch_worker import _send_email, _process_one


async def _seed_worker_data(db_session, tenant):
    carrera = Carrera(codigo="WRK-C", nombre="WorkerTest", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="WRK-M", nombre="WorkerMateria", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-W", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="worker@test.com", password_hash=hash_password("pass123!"),
        nombre="Worker", apellidos="Test", tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(user)
    return materia, user


@pytest.mark.needs_db
class TestSendEmail:
    def test_send_email_logs_and_returns_true(self, caplog):
        caplog.set_level("INFO")
        result = _send_email("test@test.com", "Asunto", "Cuerpo del mensaje")
        assert result is True
        assert "EMAIL_SIMULATED" in caplog.text


@pytest.mark.needs_db
class TestWorkerProcessOne:
    async def test_procesa_pendiente_a_enviado(self, db_session, tenant_a):
        from unittest.mock import patch

        materia, user = await _seed_worker_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        com = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="alumno@test.com",
            asunto="Test",
            cuerpo="Cuerpo",
            estado="Pendiente",
        )
        await repo.create(com)
        await db_session.commit()

        with patch("app.workers.dispatch_worker._send_email", return_value=True):
            await _process_one(db_session, com)

        await db_session.commit()
        await db_session.refresh(com)
        assert com.estado == "Enviado"
        assert com.enviado_at is not None

    async def test_falla_si_no_es_pendiente(self, db_session, tenant_a):
        materia, user = await _seed_worker_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        com = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="alumno@test.com",
            asunto="Test",
            cuerpo="Cuerpo",
            estado="Enviado",
        )
        await repo.create(com)
        await db_session.commit()

        with pytest.raises(ValueError, match="Transición inválida"):
            await _process_one(db_session, com)


@pytest.mark.needs_db
class TestWorkerBatchSize:
    async def test_get_pendientes_respeta_limit(self, db_session, tenant_a):
        materia, user = await _seed_worker_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        for i in range(5):
            com = Comunicacion(
                tenant_id=tenant_a.id,
                enviado_por=user.id,
                materia_id=materia.id,
                destinatario=f"a{i}@test.com",
                asunto=f"S{i}",
                cuerpo=f"C{i}",
                estado="Pendiente",
            )
            await repo.create(com)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=3)
        assert len(pendientes) == 3


@pytest.mark.needs_db
class TestWorkerLoteNoAprobado:
    async def test_get_pendientes_excluye_lote_no_aprobado(self, db_session, tenant_a):
        materia, user = await _seed_worker_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        com = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="lote@test.com",
            asunto="Lote no aprobado",
            cuerpo="Cuerpo",
            estado="Pendiente",
            lote_id=lote_id,
            lote_aprobado=False,
        )
        await repo.create(com)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 0

        com.lote_aprobado = True
        await repo.update(com)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 1
