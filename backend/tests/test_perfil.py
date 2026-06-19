"""Tests para C-20 Perfil: GET /api/perfil, PATCH /api/perfil."""

from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import Settings
from app.core.security import hash_password
from app.main import create_app
from app.models.user import User


@pytest.fixture
async def perfil_client_and_user(test_engine, tenant_a, db_session):
    """Client with a regular user (no special permissions)."""
    settings = Settings()

    user = User(
        email="perfil_test@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Perfil",
        apellidos="Test",
        dni="12345678",
        cuil="20-12345678-9",
        cbu="0000000000000000000001",
        alias_cbu="PERFIL.ALIAS",
        banco="Galicia",
        regional="Centro",
        legajo="L-001",
        legajo_profesional="LP-001",
        facturador=True,
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = jwt.encode(
        {
            "sub": str(user.id),
            "tenant_id": str(tenant_a.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield {
                "client": client,
                "token": token,
                "user": user,
                "tenant_a_id": tenant_a.id,
            }


@pytest.fixture
async def two_users_same_tenant(test_engine, tenant_a, db_session):
    """Two users in the same tenant for email duplicate tests."""
    settings = Settings()

    user1 = User(
        email="user1_perfil@test.com",
        password_hash=hash_password("pass123!"),
        nombre="User1",
        apellidos="Perfil",
        tenant_id=tenant_a.id,
    )
    user2 = User(
        email="user2_perfil@test.com",
        password_hash=hash_password("pass123!"),
        nombre="User2",
        apellidos="Perfil",
        tenant_id=tenant_a.id,
    )
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    token_u1 = jwt.encode(
        {
            "sub": str(user1.id),
            "tenant_id": str(tenant_a.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield {
                "client": client,
                "token_u1": token_u1,
                "user1": user1,
                "user2": user2,
                "tenant_a_id": tenant_a.id,
            }


@pytest.mark.needs_db
class TestGetPerfil:
    """GET /api/perfil — usuario autenticado consulta su perfil."""

    async def test_get_perfil_ok(self, perfil_client_and_user):
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]
        user = perfil_client_and_user["user"]

        resp = await c.get(
            "/api/perfil",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == str(user.id)
        assert body["nombre"] == "Perfil"
        assert body["apellidos"] == "Test"
        assert body["email"] == "perfil_test@test.com"
        assert body["activo"] is True

    async def test_get_perfil_incluye_pii(self, perfil_client_and_user):
        """Perfil propio incluye DNI, CUIL, CBU, alias CBU descifrados."""
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]

        resp = await c.get(
            "/api/perfil",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["dni"] == "12345678"
        assert body["cuil"] == "20-12345678-9"
        assert body["cbu"] == "0000000000000000000001"
        assert body["alias_cbu"] == "PERFIL.ALIAS"

    async def test_get_perfil_sin_auth(self, async_client):
        resp = await async_client.get("/api/perfil")
        assert resp.status_code in (401, 403)


@pytest.mark.needs_db
class TestPatchPerfil:
    """PATCH /api/perfil — usuario autenticado edita su perfil."""

    async def test_update_perfil_ok(self, perfil_client_and_user):
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]

        resp = await c.patch(
            "/api/perfil",
            json={"nombre": "Carlos", "banco": "Santander", "facturador": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["nombre"] == "Carlos"
        assert body["banco"] == "Santander"
        assert body["facturador"] is True
        # Campos no modificados se conservan
        assert body["apellidos"] == "Test"
        assert body["email"] == "perfil_test@test.com"

    async def test_update_perfil_campos_no_especificados_se_conservan(self, perfil_client_and_user):
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]

        resp = await c.patch(
            "/api/perfil",
            json={"legajo": "L-999"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["legajo"] == "L-999"
        assert body["nombre"] == "Perfil"
        assert body["apellidos"] == "Test"

    async def test_update_perfil_cuil_rechazado(self, perfil_client_and_user):
        """Enviar cuil en PATCH debe dar 422 porque no está en el schema."""
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]

        resp = await c.patch(
            "/api/perfil",
            json={"cuil": "20-87654321-9"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    async def test_update_perfil_password_rechazado(self, perfil_client_and_user):
        """Enviar password en PATCH debe dar 422 porque no está en el schema."""
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]

        resp = await c.patch(
            "/api/perfil",
            json={"password": "nueva123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    async def test_update_perfil_activo_rechazado(self, perfil_client_and_user):
        """Enviar activo en PATCH debe dar 422 porque no está en el schema."""
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]

        resp = await c.patch(
            "/api/perfil",
            json={"activo": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    async def test_update_perfil_email_duplicado(self, two_users_same_tenant):
        """Cambiar email al de otro usuario existente debe dar 409."""
        c = two_users_same_tenant["client"]
        token_u1 = two_users_same_tenant["token_u1"]
        user2 = two_users_same_tenant["user2"]

        resp = await c.patch(
            "/api/perfil",
            json={"email": user2.email},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 409

    async def test_update_perfil_email_propio_mismo_ok(self, perfil_client_and_user):
        """Poner el mismo email que ya tiene debe ser OK (sin conflicto)."""
        c = perfil_client_and_user["client"]
        token = perfil_client_and_user["token"]
        user = perfil_client_and_user["user"]

        resp = await c.patch(
            "/api/perfil",
            json={"email": user.email, "nombre": "MismoEmail"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["nombre"] == "MismoEmail"

    async def test_update_perfil_sin_auth(self, async_client):
        resp = await async_client.patch("/api/perfil", json={"nombre": "X"})
        assert resp.status_code in (401, 403)
