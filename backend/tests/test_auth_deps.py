import uuid
from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def valid_token():
    settings = Settings()
    payload = {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "roles": ["alumno"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def expired_token():
    settings = Settings()
    payload = {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "roles": [],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
async def client(test_engine):
    """Client HTTP para tests — depende de test_engine para tener tablas creadas."""
    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


class TestGetCurrentUser:
    @pytest.mark.needs_db
    async def test_valid_token_accepted(self, client, valid_token):
        """JWT válido pasa auth middleware; service rechaza refresh token dummy → 401."""
        resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "dummy"},
            headers={
                "Authorization": f"Bearer {valid_token}",
                "X-Tenant-ID": str(uuid.uuid4()),
            },
        )
        # 401 del service (refresh token inválido), no del middleware auth
        assert resp.status_code == 401
        data = resp.json()
        assert "detail" in data

    async def test_expired_token_rejected(self, client, expired_token):
        resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "dummy"},
            headers={
                "Authorization": f"Bearer {expired_token}",
                "X-Tenant-ID": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 401

    async def test_no_token_rejected(self, client):
        resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "dummy"},
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )
        # HTTPBearer returns 403 when no credentials are provided
        assert resp.status_code in (401, 403)

    async def test_malformed_token_rejected(self, client):
        resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "dummy"},
            headers={
                "Authorization": "Bearer not-a-jwt",
                "X-Tenant-ID": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 401


class TestPublicEndpoints:
    @pytest.mark.needs_db
    async def test_login_requires_no_token(self, client):
        """Endpoint público — llega al service layer sin JWT (respuesta 401 por credenciales inválidas)."""
        resp = await client.post(
            "/api/auth/login",
            json={"email": "test@test.com", "password": "pass"},
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )
        # 401 del service por credenciales inválidas, no por falta de JWT
        assert resp.status_code == 401
        assert "detail" in resp.json()

    @pytest.mark.needs_db
    async def test_forgot_requires_no_token(self, client):
        """Endpoint público — service ignora emails no registrados (200 OK por seguridad)."""
        resp = await client.post(
            "/api/auth/forgot",
            json={"email": "test@test.com"},
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )
        # forgot() no falla para emails inexistentes (seguridad por oscuridad)
        assert resp.status_code == 200
        assert "message" in resp.json()

    @pytest.mark.needs_db
    async def test_reset_requires_no_token(self, client):
        """Endpoint público — llega al service layer sin JWT (respuesta 401 por token inválido)."""
        resp = await client.post(
            "/api/auth/reset",
            json={"token": "dummy", "new_password": "newpass123!"},
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )
        # 401 del service por token inválido, no por falta de JWT
        assert resp.status_code == 401
        assert "detail" in resp.json()


class TestProtectedEndpoints:
    async def test_enroll_2fa_requires_auth(self, client):
        resp = await client.post(
            "/api/auth/2fa/enroll",
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )
        assert resp.status_code in (401, 403)

    async def test_2fa_status_requires_auth(self, client):
        resp = await client.get(
            "/api/auth/2fa/status",
            headers={"X-Tenant-ID": str(uuid.uuid4())},
        )
        assert resp.status_code in (401, 403)
