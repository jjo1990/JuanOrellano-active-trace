"""Tests para audit log e impersonación (C-05)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import text

from app.core import action_codes
from app.core.config import Settings
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol
from app.models.user import User
from app.repositories.audit_log import AuditLogRepository
from app.services.audit import AuditService
from app.core.database import Base


# ── Helpers ─────────────────────────────────────────────────────────────


async def _create_audit_log_trigger(db_session):
    """Crea el trigger append-only para tests que lo necesiten."""
    await db_session.execute(text("""
        CREATE OR REPLACE FUNCTION fn_audit_log_append_only()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log es append-only: no se permiten UPDATE ni DELETE';
        END;
        $$ LANGUAGE plpgsql;
    """))
    await db_session.execute(text("""
        CREATE TRIGGER trg_audit_log_append_only
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION fn_audit_log_append_only();
    """))
    await db_session.commit()


async def _create_impersonation_permiso(db_session) -> Permiso:
    """Crea el permiso impersonacion:usar para tests."""
    p = Permiso(
        codigo="impersonacion:usar",
        descripcion="Suplantar a otro usuario para diagnóstico",
        modulo="auth",
    )
    db_session.add(p)
    await db_session.flush()
    return p


async def _create_auditoria_ver_permiso(db_session) -> Permiso:
    p = Permiso(codigo="auditoria:ver", descripcion="Ver auditoría", modulo="auditoria")
    db_session.add(p)
    await db_session.flush()
    return p


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
async def trigger_setup(test_engine, db_session):
    """Crea la tabla audit_log y el trigger append-only."""
    # La tabla ya existe porque Base.metadata incluye AuditLog
    await _create_audit_log_trigger(db_session)
    yield
    # Cleanup del trigger
    await db_session.execute(text("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log;"))
    await db_session.execute(text("DROP FUNCTION IF EXISTS fn_audit_log_append_only();"))
    await db_session.commit()


@pytest.fixture
async def seed_impersonacion(db_session, tenant_a) -> dict:
    """Crea roles ADMIN, COORDINADOR, usuario ADMIN con impersonacion:usar."""
    rol_admin = Rol(nombre="ADMIN", descripcion="Admin", tenant_id=tenant_a.id)
    db_session.add(rol_admin)
    await db_session.flush()

    perm = await _create_impersonation_permiso(db_session)
    perm_aud = await _create_auditoria_ver_permiso(db_session)

    db_session.add(RolPermiso(rol_id=rol_admin.id, permiso_id=perm.id, tenant_id=tenant_a.id))
    db_session.add(RolPermiso(rol_id=rol_admin.id, permiso_id=perm_aud.id, tenant_id=tenant_a.id))
    await db_session.flush()

    user_admin = User(
        email="admin@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user_admin)
    await db_session.flush()

    ahora = datetime.now(timezone.utc) - timedelta(days=30)
    db_session.add(UsuarioRol(
        user_id=user_admin.id, rol_id=rol_admin.id,
        fecha_desde=ahora, tenant_id=tenant_a.id,
    ))
    await db_session.flush()

    user_regular = User(
        email="regular@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Regular", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user_regular)
    await db_session.commit()

    return {
        "admin_user": user_admin,
        "regular_user": user_regular,
        "admin_token": jwt.encode(
            {"sub": str(user_admin.id), "tenant_id": str(tenant_a.id),
             "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            Settings().secret_key, algorithm=Settings().jwt_algorithm,
        ),
        "regular_token": jwt.encode(
            {"sub": str(user_regular.id), "tenant_id": str(tenant_a.id),
             "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            Settings().secret_key, algorithm=Settings().jwt_algorithm,
        ),
        "tenant_id": tenant_a.id,
    }


# ── 5.1: Crear registro via AuditService ───────────────────────────────


@pytest.fixture
async def actor_user(db_session, tenant_a) -> User:
    user = User(
        email="actor@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Actor", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.needs_db
class TestAuditService:
    async def test_crear_registro_via_service(
        self, db_session, tenant_a, actor_user,
    ):
        repo = AuditLogRepository(db_session)
        svc = AuditService(repo)
        record = await svc.log(
            actor_id=actor_user.id,
            tenant_id=tenant_a.id,
            accion=action_codes.CALIFICACIONES_IMPORTAR,
            detalle={"cantidad": 150},
            filas_afectadas=150,
        )
        assert record.id is not None
        assert record.accion == action_codes.CALIFICACIONES_IMPORTAR
        assert record.detalle == {"cantidad": 150}
        assert record.filas_afectadas == 150
        assert record.ip is None
        assert record.user_agent is None
        assert record.impersonado_id is None
        assert record.fecha_hora is not None

    async def test_registro_con_impersonacion(
        self, db_session, tenant_a, actor_user,
    ):
        user2 = User(
            email="user2@test.com",
            password_hash=hash_password("pass123!"),
            nombre="User2", apellidos="",
            tenant_id=tenant_a.id,
        )
        db_session.add(user2)
        await db_session.flush()
        repo = AuditLogRepository(db_session)
        svc = AuditService(repo)
        record = await svc.log(
            actor_id=actor_user.id,
            tenant_id=tenant_a.id,
            accion=action_codes.IMPERSONACION_INICIAR,
            impersonado_id=user2.id,
        )
        assert record.actor_id == actor_user.id
        assert record.impersonado_id == user2.id


# ── 5.2: Append-only a nivel repositorio ─────────────────────────────


@pytest.mark.needs_db
class TestAppendOnlyRepo:
    async def test_repo_no_expone_update_delete(self):
        methods = [m for m in dir(AuditLogRepository) if not m.startswith("_")]
        assert "create" in methods
        assert "list" in methods
        assert "update" not in methods
        assert "delete" not in methods


# ── 5.3, 5.4: Trigger append-only ────────────────────────────────────


@pytest.mark.needs_db
class TestTriggerAppendOnly:
    async def test_trigger_bloquea_update(
        self, test_engine, tenant_a, trigger_setup, actor_user,
    ):
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

        async with async_sessionmaker(test_engine, expire_on_commit=False)() as session:
            record = AuditLog(
                actor_id=actor_user.id,
                tenant_id=tenant_a.id,
                accion="TEST",
            )
            session.add(record)
            await session.flush()
            await session.refresh(record)

            import sqlalchemy.exc
            with pytest.raises(sqlalchemy.exc.DBAPIError):
                await session.execute(
                    text("UPDATE audit_log SET accion = 'CHANGED' WHERE id = :id"),
                    {"id": record.id},
                )
                await session.commit()

    async def test_trigger_bloquea_delete(
        self, test_engine, tenant_a, trigger_setup, actor_user,
    ):
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

        async with async_sessionmaker(test_engine, expire_on_commit=False)() as session:
            record = AuditLog(
                actor_id=actor_user.id,
                tenant_id=tenant_a.id,
                accion="TEST",
            )
            session.add(record)
            await session.flush()
            await session.refresh(record)

            import sqlalchemy.exc
            with pytest.raises(sqlalchemy.exc.DBAPIError):
                await session.execute(
                    text("DELETE FROM audit_log WHERE id = :id"),
                    {"id": record.id},
                )
                await session.commit()


# ── 5.5, 5.6, 5.11, 5.12, 5.13: Impersonación HTTP ──────────────────


@pytest.mark.needs_db
class TestImpersonationHTTP:
    async def test_iniciar_impersonacion_exitosa(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion
        target_id = data["regular_user"].id
        resp = await async_client.post(
            f"/api/auth/impersonate/{target_id}",
            headers={
                "Authorization": f"Bearer {data['admin_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

        payload = jwt.decode(
            body["access_token"], Settings().secret_key,
            algorithms=[Settings().jwt_algorithm],
        )
        assert payload.get("impersonating") is True
        assert payload.get("actor_id") == str(data["admin_user"].id)
        assert payload.get("sub") == str(target_id)

        # Verificar audit log
        repo = AuditLogRepository(db_session)
        logs = await repo.list(tenant_id=data["tenant_id"])
        acciones = [l.accion for l in logs]
        assert action_codes.IMPERSONACION_INICIAR in acciones

    async def test_sin_permiso_devuelve_403(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion
        resp = await async_client.post(
            f"/api/auth/impersonate/{data['admin_user'].id}",
            headers={
                "Authorization": f"Bearer {data['regular_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 403

    async def test_usuario_inexistente_devuelve_404(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion
        fake_id = uuid.uuid4()
        resp = await async_client.post(
            f"/api/auth/impersonate/{fake_id}",
            headers={
                "Authorization": f"Bearer {data['admin_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 404

    async def test_finalizar_impersonacion(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion
        target_id = data["regular_user"].id

        # Start impersonation
        start_resp = await async_client.post(
            f"/api/auth/impersonate/{target_id}",
            headers={
                "Authorization": f"Bearer {data['admin_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        imp_token = start_resp.json()["access_token"]

        # Stop impersonation
        resp = await async_client.post(
            "/api/auth/impersonate/stop",
            headers={
                "Authorization": f"Bearer {imp_token}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

        payload = jwt.decode(
            body["access_token"], Settings().secret_key,
            algorithms=[Settings().jwt_algorithm],
        )
        assert payload.get("impersonating") is None
        assert payload.get("sub") == str(data["admin_user"].id)

        # Verify audit log
        repo = AuditLogRepository(db_session)
        logs = await repo.list(tenant_id=data["tenant_id"])
        acciones = [l.accion for l in logs]
        assert action_codes.IMPERSONACION_FINALIZAR in acciones

    async def test_stop_sin_impersonacion_activa_devuelve_400(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion
        resp = await async_client.post(
            "/api/auth/impersonate/stop",
            headers={
                "Authorization": f"Bearer {data['admin_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 400
        assert "No hay impersonación activa" in resp.json()["detail"]


# ── 5.7, 5.8: Atribución bajo impersonación ──────────────────────────


@pytest.mark.needs_db
class TestImpersonacionAtribucion:
    async def test_accion_bajo_impersonacion_registra_actor_e_impersonado(
        self, db_session, tenant_a, actor_user,
    ):
        user2 = User(
            email="user2b@test.com",
            password_hash=hash_password("pass123!"),
            nombre="User2B", apellidos="",
            tenant_id=tenant_a.id,
        )
        db_session.add(user2)
        await db_session.flush()
        repo = AuditLogRepository(db_session)
        svc = AuditService(repo)
        record = await svc.log(
            actor_id=actor_user.id,
            tenant_id=tenant_a.id,
            accion=action_codes.CALIFICACIONES_IMPORTAR,
            impersonado_id=user2.id,
        )
        assert record.actor_id == actor_user.id
        assert record.impersonado_id == user2.id

    async def test_accion_sin_impersonacion_registra_actor_y_null(
        self, db_session, tenant_a, actor_user,
    ):
        repo = AuditLogRepository(db_session)
        svc = AuditService(repo)
        record = await svc.log(
            actor_id=actor_user.id,
            tenant_id=tenant_a.id,
            accion=action_codes.CALIFICACIONES_IMPORTAR,
        )
        assert record.actor_id == actor_user.id
        assert record.impersonado_id is None


# ── 5.9, 5.10: GET /audit-log ────────────────────────────────────────


@pytest.mark.needs_db
class TestAuditLogEndpoint:
    async def test_listar_con_filtros(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion

        # Crear algunos registros
        repo = AuditLogRepository(db_session)
        svc = AuditService(repo)
        await svc.log(
            actor_id=data["admin_user"].id,
            tenant_id=data["tenant_id"],
            accion=action_codes.CALIFICACIONES_IMPORTAR,
        )
        await svc.log(
            actor_id=data["admin_user"].id,
            tenant_id=data["tenant_id"],
            accion=action_codes.PADRON_CARGAR,
        )
        await db_session.commit()

        resp = await async_client.get(
            "/api/audit-log",
            headers={
                "Authorization": f"Bearer {data['admin_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) == 2
        assert body["limit"] == 50
        assert body["offset"] == 0

        resp = await async_client.get(
            f"/api/audit-log?accion={action_codes.CALIFICACIONES_IMPORTAR}",
            headers={
                "Authorization": f"Bearer {data['admin_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["items"]) == 1
        assert body["items"][0]["accion"] == action_codes.CALIFICACIONES_IMPORTAR

    async def test_sin_permiso_auditoria_ver_devuelve_403(
        self, db_session, tenant_a, seed_impersonacion, async_client,
    ):
        data = seed_impersonacion
        resp = await async_client.get(
            "/api/audit-log",
            headers={
                "Authorization": f"Bearer {data['regular_token']}",
                "X-Tenant-ID": str(data["tenant_id"]),
            },
        )
        assert resp.status_code == 403
