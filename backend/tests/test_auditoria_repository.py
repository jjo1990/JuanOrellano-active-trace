"""Tests para AuditoriaRepository — metodos de agregacion (C-19)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.materia import Materia
from app.models.user import User
from app.repositories.audit_log import AuditLogRepository


async def _seed_audit_logs(db_session, tenant, n=5):
    user = User(
        email=f"auditoria_repo_{uuid.uuid4().hex[:6]}@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Repo", apellidos="User",
        tenant_id=tenant.id,
    )
    db_session.add(user)
    materia = Materia(codigo=f"MAT-{uuid.uuid4().hex[:6]}", nombre="RepoMateria", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    records = []
    for i in range(n):
        rec = AuditLog(
            tenant_id=tenant.id,
            actor_id=user.id,
            materia_id=materia.id,
            accion="CALIFICACIONES_IMPORTAR",
            detalle={"count": i},
            filas_afectadas=i * 10,
            fecha_hora=now - timedelta(days=i),
        )
        db_session.add(rec)
        records.append(rec)
    await db_session.flush()
    return records, user, materia


@pytest.mark.needs_db
class TestListWithFilters:
    async def test_list_with_filters_sin_filtros(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.list_with_filters(tenant_id=tenant_a.id)
        assert len(result) == 3

    async def test_list_with_filters_por_materia(self, db_session, tenant_a):
        records, _, materia = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.list_with_filters(
            tenant_id=tenant_a.id, materia_id=materia.id,
        )
        assert len(result) == 3
        assert all(r.materia_id == materia.id for r in result)

    async def test_list_with_filters_por_materia_ids(self, db_session, tenant_a):
        records, _, materia = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.list_with_filters(
            tenant_id=tenant_a.id, materia_ids=[materia.id],
        )
        assert len(result) == 3

    async def test_list_with_filters_materia_ids_vacio(self, db_session, tenant_a):
        await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.list_with_filters(
            tenant_id=tenant_a.id, materia_ids=[],
        )
        assert len(result) == 0

    async def test_list_with_filters_limite_offset(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=5)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.list_with_filters(
            tenant_id=tenant_a.id, limit=2, offset=1,
        )
        assert len(result) == 2


@pytest.mark.needs_db
class TestCountByDate:
    async def test_count_by_date_agrupa_por_fecha_accion(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.count_by_date(tenant_id=tenant_a.id)
        assert len(result) >= 1
        for row in result:
            assert "fecha" in row
            assert "accion" in row
            assert "cantidad" in row
            assert row["cantidad"] >= 1

    async def test_count_by_date_con_rango(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=5)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        desde = datetime.now(timezone.utc) - timedelta(days=2)
        hasta = datetime.now(timezone.utc) + timedelta(days=1)
        result = await repo.count_by_date(
            tenant_id=tenant_a.id, fecha_desde=desde, fecha_hasta=hasta,
        )
        assert len(result) >= 1


@pytest.mark.needs_db
class TestCountByDocenteAccion:
    async def test_count_by_docente_accion_agrupa(self, db_session, tenant_a):
        records, user, _ = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.count_by_docente_accion(tenant_id=tenant_a.id)
        assert len(result) >= 1
        for row in result:
            assert "docente_id" in row
            assert row["docente_id"] == user.id
            assert "accion" in row
            assert "cantidad" in row

    async def test_count_by_docente_accion_con_filtro_materia(self, db_session, tenant_a):
        records, user, materia = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        result = await repo.count_by_docente_accion(
            tenant_id=tenant_a.id, materia_ids=[materia.id],
        )
        assert len(result) >= 1


@pytest.mark.needs_db
class TestCountByEstadoComunicacion:
    async def test_cuenta_comunicaciones_por_estado(self, db_session, tenant_a):
        user = User(
            email=f"com_estado_{uuid.uuid4().hex[:6]}@test.com",
            password_hash=hash_password("pass123!"),
            nombre="Com", apellidos="User",
            tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()

        rec = AuditLog(
            tenant_id=tenant_a.id,
            actor_id=user.id,
            accion="COMUNICACION_ENVIAR",
            detalle={"accion": "aprobar_lote", "lote_id": str(uuid.uuid4()), "afectadas": 5},
            fecha_hora=datetime.now(timezone.utc),
        )
        db_session.add(rec)
        rec2 = AuditLog(
            tenant_id=tenant_a.id,
            actor_id=user.id,
            accion="COMUNICACION_ENVIAR",
            detalle={"accion": "cancelar_lote", "lote_id": str(uuid.uuid4()), "afectadas": 2},
            fecha_hora=datetime.now(timezone.utc),
        )
        db_session.add(rec2)
        await db_session.commit()

        repo = AuditLogRepository(db_session)
        result = await repo.count_by_estado_comunicacion(tenant_id=tenant_a.id)
        assert len(result) >= 2
        estados = {r["estado"] for r in result}
        assert "aprobar_lote" in estados
        assert "cancelar_lote" in estados

    async def test_no_incluye_otras_acciones(self, db_session, tenant_a):
        user = User(
            email=f"filtro_com_{uuid.uuid4().hex[:6]}@test.com",
            password_hash=hash_password("pass123!"),
            nombre="Filtro", apellidos="User",
            tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()

        db_session.add(AuditLog(
            tenant_id=tenant_a.id,
            actor_id=user.id,
            accion="CALIFICACIONES_IMPORTAR",
            fecha_hora=datetime.now(timezone.utc),
        ))
        await db_session.commit()

        repo = AuditLogRepository(db_session)
        result = await repo.count_by_estado_comunicacion(tenant_id=tenant_a.id)
        for row in result:
            assert row["estado"] is not None


@pytest.mark.needs_db
class TestCountWithFilters:
    async def test_count_with_filters_total(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        total = await repo.count_with_filters(tenant_id=tenant_a.id)
        assert total == 3

    async def test_count_with_filters_por_accion(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        total = await repo.count_with_filters(
            tenant_id=tenant_a.id, accion="CALIFICACIONES_IMPORTAR",
        )
        assert total == 3

    async def test_count_con_materia_ids_vacio(self, db_session, tenant_a):
        records, _, _ = await _seed_audit_logs(db_session, tenant_a, n=3)
        await db_session.commit()
        repo = AuditLogRepository(db_session)
        total = await repo.count_with_filters(
            tenant_id=tenant_a.id, materia_ids=[],
        )
        assert total == 0
