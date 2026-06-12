"""Tests para ComunicacionService (C-12) — Strict TDD."""

import uuid
from datetime import date

import pytest

from app.core.action_codes import COMUNICACION_ENVIAR
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.comunicacion import Comunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.schemas.comunicacion import CancelarRequest, EnviarRequest, PreviewRequest
from app.services.comunicacion_service import ComunicacionService


async def _seed_service_data(db_session, tenant):
    carrera = Carrera(codigo="COM-SVC", nombre="ComService", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(
        codigo="MAT-SVC", nombre="Algoritmos I", tenant_id=tenant.id,
    )
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-S", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="svcuser@test.com", password_hash=hash_password("pass123!"),
        nombre="Svc", apellidos="User", tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.flush()
    version = VersionPadron(
        tenant_id=tenant.id,
        materia_id=materia.id, cohorte_id=cohorte.id,
        cargado_por=user.id, activa=True,
    )
    db_session.add(version)
    await db_session.flush()

    entradas = []
    for i in range(3):
        entrada = EntradaPadron(
            tenant_id=tenant.id,
            version_id=version.id,
            nombre=f"Alumno{i}",
            apellidos=f"Apellido{i}",
            email=f"alumno{i}@test.com",
        )
        db_session.add(entrada)
        await db_session.flush()
        entradas.append(entrada)

    await db_session.commit()
    for e in entradas:
        await db_session.refresh(e)
    await db_session.refresh(materia)
    await db_session.refresh(user)
    return materia, user, entradas, version


@pytest.mark.needs_db
class TestComunicacionServicePreview:
    async def test_preview_renderiza_para_un_alumno(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = PreviewRequest(
            template="Hola {{nombre}}, materia: {{materia}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
        )
        result = await svc.preview(request)
        assert len(result.previews) == 1
        preview = result.previews[0]
        assert preview.alumno_id == entradas[0].id
        assert "Alumno0" in preview.cuerpo
        assert "Algoritmos I" in preview.cuerpo

    async def test_preview_no_persiste(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        from sqlalchemy import select as sa_select

        stmt = sa_select(Comunicacion).where(
            Comunicacion.tenant_id == tenant_a.id,
        )
        before = (await db_session.execute(stmt)).scalars().all()
        assert len(before) == 0

        request = PreviewRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
        )
        await svc.preview(request)

        after = (await db_session.execute(stmt)).scalars().all()
        assert len(after) == 0

    async def test_preview_con_alumno_sin_datos(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = PreviewRequest(
            template="Hola {{nombre}}, pendientes: {{actividades_pendientes}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
        )
        result = await svc.preview(request)
        assert len(result.previews) == 1
        assert "Alumno0" in result.previews[0].cuerpo
        assert "{{actividades_pendientes}}" in result.previews[0].cuerpo

    async def test_preview_multiples_alumnos(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = PreviewRequest(
            template="Hola {{nombre}}",
            alumno_ids=[e.id for e in entradas[:2]],
            materia_id=materia.id,
        )
        result = await svc.preview(request)
        assert len(result.previews) == 2


@pytest.mark.needs_db
class TestComunicacionServiceEnviar:
    async def test_enviar_crea_comunicaciones_con_lote(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[e.id for e in entradas],
            materia_id=materia.id,
            asunto="Recordatorio {{materia}}",
        )
        result = await svc.enviar(request, user.id)

        assert result.count == 3
        assert result.estado == "Pendiente"
        assert result.lote_id is not None

        from sqlalchemy import select as sa_select

        stmt = sa_select(Comunicacion).where(
            Comunicacion.lote_id == result.lote_id,
            Comunicacion.tenant_id == tenant_a.id,
            Comunicacion.deleted_at.is_(None),
        )
        comunicaciones = (await db_session.execute(stmt)).scalars().all()
        assert len(comunicaciones) == 3
        for c in comunicaciones:
            assert c.estado == "Pendiente"

    async def test_enviar_renderiza_por_alumno(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id, entradas[1].id],
            materia_id=materia.id,
            asunto="Aviso {{materia}}",
        )
        result = await svc.enviar(request, user.id)

        from sqlalchemy import select as sa_select

        stmt = sa_select(Comunicacion).where(
            Comunicacion.lote_id == result.lote_id,
            Comunicacion.tenant_id == tenant_a.id,
            Comunicacion.deleted_at.is_(None),
        ).order_by(Comunicacion.created_at)
        comunicaciones = (await db_session.execute(stmt)).scalars().all()

        cuerpos = {c.cuerpo for c in comunicaciones}
        assert any("Alumno0" in c for c in cuerpos)
        assert any("Alumno1" in c for c in cuerpos)

    async def test_enviar_registra_auditoria(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
            asunto="Test",
        )
        await svc.enviar(request, user.id)

        from sqlalchemy import select as sa_select

        stmt = sa_select(AuditLog).where(
            AuditLog.tenant_id == tenant_a.id,
            AuditLog.accion == COMUNICACION_ENVIAR,
        )
        logs = (await db_session.execute(stmt)).scalars().all()
        assert len(logs) >= 1

    async def test_enviar_lotes_diferentes_son_independientes(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        req1 = EnviarRequest(
            template="Lote 1 {{nombre}}",
            alumno_ids=[entradas[1].id],
            materia_id=materia.id,
            asunto="L1",
        )
        req2 = EnviarRequest(
            template="Lote 2 {{nombre}}",
            alumno_ids=[entradas[2].id],
            materia_id=materia.id,
            asunto="L2",
        )
        r1 = await svc.enviar(req1, user.id)
        r2 = await svc.enviar(req2, user.id)
        assert r1.lote_id != r2.lote_id


@pytest.mark.needs_db
class TestComunicacionServiceAprobarLote:
    async def test_aprobar_lote_transiciona_flag(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id, entradas[1].id],
            materia_id=materia.id,
            asunto="Test",
        )
        envio = await svc.enviar(request, user.id)

        result = await svc.aprobar_lote(envio.lote_id, user.id)
        assert result.resumen.get("pendientes", 0) == 2

        from sqlalchemy import select as sa_select

        stmt = sa_select(Comunicacion).where(
            Comunicacion.lote_id == envio.lote_id,
            Comunicacion.tenant_id == tenant_a.id,
            Comunicacion.deleted_at.is_(None),
        )
        comunicaciones = (await db_session.execute(stmt)).scalars().all()
        for c in comunicaciones:
            assert c.lote_aprobado is True


@pytest.mark.needs_db
class TestComunicacionServiceCancelar:
    async def test_cancelar_individual(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
            asunto="Test",
        )
        envio = await svc.enviar(request, user.id)

        from sqlalchemy import select as sa_select

        stmt = sa_select(Comunicacion).where(
            Comunicacion.lote_id == envio.lote_id,
            Comunicacion.tenant_id == tenant_a.id,
            Comunicacion.deleted_at.is_(None),
        )
        comunicaciones = (await db_session.execute(stmt)).scalars().all()
        com_id = comunicaciones[0].id

        result = await svc.cancelar_individual(com_id, user.id)
        assert result.estado == "Cancelado"

    async def test_cancelar_individual_falla_si_no_pendiente(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        com = Comunicacion(
            tenant_id=tenant_a.id,
            enviado_por=user.id,
            materia_id=materia.id,
            destinatario="x@test.com",
            asunto="X",
            cuerpo="Y",
            estado="Enviado",
        )
        from app.repositories.comunicacion_repository import ComunicacionRepository
        repo = ComunicacionRepository(db_session, tenant_a.id)
        created = await repo.create(com)
        await db_session.commit()

        with pytest.raises(ValueError, match="Transición inválida"):
            await svc.cancelar_individual(created.id, user.id)

    async def test_cancelar_lote(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id, entradas[1].id],
            materia_id=materia.id,
            asunto="Test",
        )
        envio = await svc.enviar(request, user.id)

        result = await svc.cancelar_lote(envio.lote_id, user.id)
        assert result.resumen.get("cancelados", 0) == 2


@pytest.mark.needs_db
class TestComunicacionServiceConsultas:
    async def test_get_lote_status(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
            asunto="Test",
        )
        envio = await svc.enviar(request, user.id)

        status = await svc.get_lote_status(envio.lote_id)
        assert status.lote_id == envio.lote_id
        assert len(status.comunicaciones) == 1
        assert status.resumen.get("pendientes", 0) == 1

    async def test_get_by_materia(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
            asunto="Test",
        )
        await svc.enviar(request, user.id)

        resultados = await svc.get_by_materia(materia.id)
        assert len(resultados) == 1

    async def test_get_by_materia_filtra_estado(self, db_session, tenant_a):
        materia, user, entradas, _ = await _seed_service_data(db_session, tenant_a)
        svc = ComunicacionService(db_session, tenant_a.id)

        request = EnviarRequest(
            template="Hola {{nombre}}",
            alumno_ids=[entradas[0].id],
            materia_id=materia.id,
            asunto="Test",
        )
        await svc.enviar(request, user.id)

        pendientes = await svc.get_by_materia(materia.id, estado="Pendiente")
        assert len(pendientes) == 1

        enviados = await svc.get_by_materia(materia.id, estado="Enviado")
        assert len(enviados) == 0
