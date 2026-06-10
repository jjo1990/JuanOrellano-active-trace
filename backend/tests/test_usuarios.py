"""Tests para C-07 usuarios: PII cifrada, unicidad, activo/inactivo."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import select

from app.core.config import Settings
from app.core.security import hash_password
from app.main import create_app
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user import User
from app.models.usuario_rol import UsuarioRol


@pytest.fixture
async def admin_usuarios_client_and_data(test_engine, tenant_a, tenant_b, db_session):
    """Client with a seeded ADMIN user that has 'usuarios:gestionar' permission."""
    settings = Settings()

    admin_rol = Rol(
        nombre="ADMIN_USUARIOS", descripcion="Admin for user tests",
        tenant_id=tenant_a.id,
    )
    db_session.add(admin_rol)
    await db_session.flush()

    perm = Permiso(
        codigo="usuarios:gestionar",
        descripcion="Gestionar usuarios",
        modulo="usuarios",
    )
    db_session.add(perm)
    await db_session.flush()

    rp = RolPermiso(rol_id=admin_rol.id, permiso_id=perm.id, tenant_id=tenant_a.id)
    db_session.add(rp)

    user = User(
        email="admin_user@test.com", password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="Usuarios", tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()

    ur = UsuarioRol(
        user_id=user.id, rol_id=admin_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)
    await db_session.commit()

    admin_token = jwt.encode(
        {"sub": str(user.id), "tenant_id": str(tenant_a.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )

    app = create_app()

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield {
                "client": client,
                "admin_token": admin_token,
                "tenant_a_id": tenant_a.id,
                "tenant_b_id": tenant_b.id,
            }


@pytest.mark.needs_db
class TestPIIEncryption:
    """9.1: PII cifrada en DB — dni, cuil, cbu, alias_cbu se almacenan cifrados."""

    async def test_pii_cifrada_en_db(self, test_engine, tenant_a, db_session):
        user = User(
            email="pii_test@test.com", password_hash="hash",
            nombre="PII", apellidos="Test",
            dni="12345678", cuil="20-12345678-9",
            cbu="0000000000000000000001", alias_cbu="PII.ALIAS",
            tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Leer raw desde DB
        stmt = select(
            User.dni_encrypted, User.cuil_encrypted,
            User.cbu_encrypted, User.alias_cbu_encrypted,
        ).where(User.id == user.id)
        result = await db_session.execute(stmt)
        row = result.one()

        assert row.dni_encrypted is not None
        assert row.dni_encrypted != "12345678"
        assert row.cuil_encrypted is not None
        assert row.cuil_encrypted != "20-12345678-9"
        assert row.cbu_encrypted is not None
        assert row.cbu_encrypted != "0000000000000000000001"
        assert row.alias_cbu_encrypted is not None
        assert row.alias_cbu_encrypted != "PII.ALIAS"

        # Leer via descriptor (se descifra automáticamente)
        assert user.dni == "12345678"
        assert user.cuil == "20-12345678-9"
        assert user.cbu == "0000000000000000000001"
        assert user.alias_cbu == "PII.ALIAS"


@pytest.mark.needs_db
class TestResponseNoPII:
    """9.2: Response de usuario NO expone PII."""

    async def test_response_no_expone_pii(self, admin_usuarios_client_and_data, db_session, tenant_a):
        c = admin_usuarios_client_and_data["client"]
        token = admin_usuarios_client_and_data["admin_token"]
        t_a = admin_usuarios_client_and_data["tenant_a_id"]

        # POST
        resp = await c.post(
            "/api/admin/usuarios",
            json={
                "nombre": "Juan", "apellidos": "Perez",
                "email": "juan@test.com", "password": "pass12345",
                "dni": "12345678", "cuil": "20-12345678-9",
                "cbu": "0000000000000000001", "alias_cbu": "JUAN.ALIAS",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "dni" not in body
        assert "cuil" not in body
        assert "cbu" not in body
        assert "alias_cbu" not in body
        assert body["nombre"] == "Juan"
        assert body["apellidos"] == "Perez"
        assert body["email"] == "juan@test.com"

        # GET
        user_id = body["id"]
        resp = await c.get(
            f"/api/admin/usuarios/{user_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "dni" not in body
        assert "cuil" not in body


@pytest.mark.needs_db
class TestEmailUniqueness:
    """9.3-9.4: Unicidad (tenant_id, email)."""

    async def test_mismo_email_mismo_tenant_409(self, admin_usuarios_client_and_data):
        c = admin_usuarios_client_and_data["client"]
        token = admin_usuarios_client_and_data["admin_token"]
        t_a = admin_usuarios_client_and_data["tenant_a_id"]

        payload = {
            "nombre": "A", "apellidos": "B",
            "email": "dupe@test.com", "password": "pass12345",
        }
        resp = await c.post(
            "/api/admin/usuarios", json=payload,
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 201

        resp = await c.post(
            "/api/admin/usuarios", json=payload,
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 409

    async def test_mismo_email_distinto_tenant_ok(self, admin_usuarios_client_and_data):
        c = admin_usuarios_client_and_data["client"]
        token = admin_usuarios_client_and_data["admin_token"]
        t_a = admin_usuarios_client_and_data["tenant_a_id"]
        t_b = admin_usuarios_client_and_data["tenant_b_id"]

        payload_a = {
            "nombre": "A", "apellidos": "Cross",
            "email": "cross@test.com", "password": "pass12345",
        }
        resp = await c.post(
            "/api/admin/usuarios", json=payload_a,
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 201

        payload_b = {
            "nombre": "B", "apellidos": "Cross",
            "email": "cross@test.com", "password": "pass12345",
        }

        # Need admin in tenant_b too
        settings = Settings()
        from app.models.rol import Rol as RolModel
        from app.models.permiso import Permiso as PermisoModel
        from app.models.rol_permiso import RolPermiso as RolPermisoModel
        from app.models.usuario_rol import UsuarioRol as UsuarioRolModel

        admin_rol_b = RolModel(
            nombre="ADMIN_B_USER", descripcion="Admin B", tenant_id=t_b,
        )
        db_session = None  # Will get from fixture
        # Use the test's db_session via the fixture

        # Actually simpler: use the existing db_session from test_engine
        from sqlalchemy.ext.asyncio import async_sessionmaker
        from app.core.database import create_engine

        engine = create_engine(Settings().database_url)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with session_factory() as local_session:
            admin_rol_b = RolModel(nombre="ADMIN_B_USER", descripcion="Admin B", tenant_id=t_b)
            local_session.add(admin_rol_b)
            await local_session.flush()

            perm = await local_session.execute(
                select(Permiso).where(Permiso.codigo == "usuarios:gestionar")
            )
            perm = perm.scalar_one()
            rp_b = RolPermisoModel(rol_id=admin_rol_b.id, permiso_id=perm.id, tenant_id=t_b)
            local_session.add(rp_b)

            user_b = User(
                email="admin_b_user@test.com", password_hash=hash_password("pass123!"),
                nombre="Admin", apellidos="B", tenant_id=t_b,
            )
            local_session.add(user_b)
            await local_session.flush()

            ur_b = UsuarioRolModel(
                user_id=user_b.id, rol_id=admin_rol_b.id,
                fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
                tenant_id=t_b,
            )
            local_session.add(ur_b)
            await local_session.commit()

            token_b = jwt.encode(
                {"sub": str(user_b.id), "tenant_id": str(t_b),
                 "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
                settings.secret_key, algorithm=settings.jwt_algorithm,
            )

            resp = await c.post(
                "/api/admin/usuarios", json=payload_b,
                headers={"Authorization": f"Bearer {token_b}", "X-Tenant-ID": str(t_b)},
            )
            assert resp.status_code == 201


@pytest.mark.needs_db
class TestUsuarioInactivo:
    """9.12: Usuario inactivo no puede hacer login."""

    async def test_usuario_inactivo_login_falla(self, admin_usuarios_client_and_data, db_session, tenant_a):
        c = admin_usuarios_client_and_data["client"]
        token = admin_usuarios_client_and_data["admin_token"]
        t_a = admin_usuarios_client_and_data["tenant_a_id"]

        # Crear usuario
        resp = await c.post(
            "/api/admin/usuarios",
            json={
                "nombre": "Inactivo", "apellidos": "Test",
                "email": "inactivo@test.com", "password": "pass12345",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 201
        user_id = resp.json()["id"]

        # PATCH status a inactivo
        resp = await c.patch(
            f"/api/admin/usuarios/{user_id}/status",
            json={"activo": False},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 200
        assert resp.json()["activo"] is False

        # Intentar login — falls because user is inactive
        resp = await c.post(
            "/api/auth/login",
            json={"email": "inactivo@test.com", "password": "pass12345"},
            headers={"X-Tenant-ID": str(t_a)},
        )
        assert resp.status_code == 401
