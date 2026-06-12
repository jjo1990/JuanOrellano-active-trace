"""Tests para ComunicacionRepository (C-12)."""

import uuid
from datetime import date

import pytest

from app.core.security import hash_password
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.comunicacion import Comunicacion
from app.models.materia import Materia
from app.models.user import User
from app.repositories.comunicacion_repository import ComunicacionRepository


async def _seed_comunicacion_data(db_session, tenant):
    carrera = Carrera(codigo="COM-REPO", nombre="ComunicacionRepo", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-COM", nombre="MateriaComunicacion", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-C", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="comrepo@test.com", password_hash=hash_password("pass123!"),
        nombre="ComRepo", apellidos="User", tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(user)
    return materia, user


@pytest.mark.needs_db
class TestComunicacionRepositoryGetPendientes:
    async def test_get_pendientes_retorna_solo_pendientes(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
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

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 1
        assert pendientes[0].estado == "Pendiente"

    async def test_get_pendientes_no_retorna_otros_estados(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        com_enviado = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="alumno1@test.com",
            asunto="Test",
            cuerpo="Cuerpo",
            estado="Enviado",
        )
        await repo.create(com_enviado)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 0

    async def test_get_pendientes_respeta_limit(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        for i in range(5):
            com = Comunicacion(
                tenant_id=tenant_a.id,
                enviado_por=user.id,
                materia_id=materia.id,
                destinatario=f"alumno{i}@test.com",
                asunto=f"Test {i}",
                cuerpo=f"Cuerpo {i}",
                estado="Pendiente",
            )
            await repo.create(com)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=3)
        assert len(pendientes) == 3

    async def test_get_pendientes_excluye_lotes_no_aprobados(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        com_lote = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="alumno@test.com",
            asunto="Test lote",
            cuerpo="Cuerpo lote",
            estado="Pendiente",
            lote_id=lote_id,
            lote_aprobado=False,
        )
        await repo.create(com_lote)

        com_sin_lote = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="alumno2@test.com",
            asunto="Test sin lote",
            cuerpo="Cuerpo sin lote",
            estado="Pendiente",
        )
        await repo.create(com_sin_lote)
        await db_session.commit()

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 1
        assert pendientes[0].lote_id is None


@pytest.mark.needs_db
class TestComunicacionRepositoryGetByLote:
    async def test_get_by_lote_retorna_todas_del_lote(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        for i in range(3):
            com = Comunicacion(
                tenant_id=tenant_a.id,
                enviado_por=user.id,
                materia_id=materia.id,
                destinatario=f"alumno{i}@test.com",
                asunto=f"Lote {i}",
                cuerpo=f"Cuerpo {i}",
                estado="Pendiente",
                lote_id=lote_id,
            )
            await repo.create(com)
        await db_session.commit()

        resultados = await repo.get_by_lote(lote_id)
        assert len(resultados) == 3

    async def test_get_by_lote_excluye_deleted(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        com1 = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="a@test.com",
            asunto="S1",
            cuerpo="C1",
            estado="Pendiente",
            lote_id=lote_id,
        )
        com2 = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="b@test.com",
            asunto="S2",
            cuerpo="C2",
            estado="Pendiente",
            lote_id=lote_id,
        )
        await repo.create(com1)
        await repo.create(com2)
        await db_session.commit()

        await repo.soft_delete(com1.id)
        await db_session.commit()

        resultados = await repo.get_by_lote(lote_id)
        assert len(resultados) == 1

    async def test_get_by_lote_lote_inexistente(self, db_session, tenant_a):
        repo = ComunicacionRepository(db_session, tenant_a.id)
        resultados = await repo.get_by_lote(uuid.uuid4())
        assert len(resultados) == 0


@pytest.mark.needs_db
class TestComunicacionRepositoryGetByMateria:
    async def test_get_by_materia_todas(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        for estado in ["Pendiente", "Enviado", "Error"]:
            com = Comunicacion(
                tenant_id=tenant_a.id,
                enviado_por=user.id,
                materia_id=materia.id,
                destinatario="a@test.com",
                asunto=f"T-{estado}",
                cuerpo=f"C-{estado}",
                estado=estado,
            )
            await repo.create(com)
        await db_session.commit()

        resultados = await repo.get_by_materia(materia.id)
        assert len(resultados) == 3

    async def test_get_by_materia_filtra_por_estado(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        for estado in ["Pendiente", "Enviado", "Error"]:
            com = Comunicacion(
                tenant_id=tenant_a.id,
                enviado_por=user.id,
                materia_id=materia.id,
                destinatario="a@test.com",
                asunto=f"T-{estado}",
                cuerpo=f"C-{estado}",
                estado=estado,
            )
            await repo.create(com)
        await db_session.commit()

        enviados = await repo.get_by_materia(materia.id, estado="Enviado")
        assert len(enviados) == 1
        assert enviados[0].estado == "Enviado"

    async def test_get_by_materia_sin_resultados(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)
        resultados = await repo.get_by_materia(materia.id, estado="Cancelado")
        assert len(resultados) == 0


@pytest.mark.needs_db
class TestComunicacionRepositoryAprobarLote:
    async def test_aprobar_lote_actualiza_flag(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        for i in range(2):
            com = Comunicacion(
                tenant_id=tenant_a.id,
                enviado_por=user.id,
                materia_id=materia.id,
                destinatario=f"a{i}@test.com",
                asunto=f"S{i}",
                cuerpo=f"C{i}",
                estado="Pendiente",
                lote_id=lote_id,
                lote_aprobado=False,
            )
            await repo.create(com)
        await db_session.commit()

        count = await repo.aprobar_lote(lote_id)
        assert count == 2

        pendientes = await repo.get_pendientes(limit=10)
        assert len(pendientes) == 2


@pytest.mark.needs_db
class TestComunicacionRepositoryCancelarLote:
    async def test_cancelar_lote_solo_pendientes(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        lote_id = uuid.uuid4()
        com_pend = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="pend@test.com",
            asunto="P",
            cuerpo="C",
            estado="Pendiente",
            lote_id=lote_id,
        )
        com_env = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="env@test.com",
            asunto="E",
            cuerpo="C",
            estado="Enviado",
            lote_id=lote_id,
        )
        await repo.create(com_pend)
        await repo.create(com_env)
        await db_session.commit()

        count = await repo.cancelar_lote(lote_id)
        assert count == 1

        await db_session.refresh(com_pend)
        assert com_pend.estado == "Cancelado"

        await db_session.refresh(com_env)
        assert com_env.estado == "Enviado"


@pytest.mark.needs_db
class TestComunicacionRepositoryEncryptedField:
    async def test_destinatario_se_cifra_y_descifra(self, db_session, tenant_a):
        materia, user = await _seed_comunicacion_data(db_session, tenant_a)
        repo = ComunicacionRepository(db_session, tenant_a.id)

        email = "alumno@test.com"
        com = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario=email,
            asunto="Test",
            cuerpo="Cuerpo",
            estado="Pendiente",
        )
        created = await repo.create(com)
        await db_session.commit()

        assert created.destinatario_encrypted != email
        assert created.destinatario == email

        retrieved = await repo.get(created.id)
        assert retrieved.destinatario == email
