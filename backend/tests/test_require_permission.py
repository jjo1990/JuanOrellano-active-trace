"""Tests RED para require_permission (Grupo 3)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import Settings
from app.main import create_app
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
async def rbac_client(test_engine, tenant_a, db_session):
    """Client with seeded RBAC data and a user with known permissions."""
    settings = Settings()

    # Crear rol ADMIN
    admin_rol = Rol(nombre="ADMIN", descripcion="Admin", tenant_id=tenant_a.id)
    db_session.add(admin_rol)
    await db_session.flush()

    # Crear permiso
    perm = Permiso(
        codigo="test:acceder",
        descripcion="Test access",
        modulo="test",
    )
    db_session.add(perm)
    await db_session.flush()

    # Asignar permiso al rol
    rp = RolPermiso(
        rol_id=admin_rol.id,
        permiso_id=perm.id,
        tenant_id=tenant_a.id,
    )
    db_session.add(rp)

    # Crear usuario
    user = User(
        email="admin@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()

    # Asignar rol al usuario
    ur = UsuarioRol(
        user_id=user.id,
        rol_id=admin_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)
    await db_session.commit()

    # Crear token JWT (sin roles, slimmed down)
    token = jwt.encode(
        {
            "sub": str(user.id),
            "tenant_id": str(tenant_a.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    # Crear app con un endpoint protegido de prueba
    from fastapi import APIRouter, Depends

    from app.core.dependencies import require_permission, get_db, get_current_user
    from sqlalchemy.ext.asyncio import AsyncSession

    app = create_app()
    test_router = APIRouter()

    @test_router.get("/test/protegido")
    async def endpoint_protegido(
        user=Depends(require_permission("test:acceder")),
        db: AsyncSession = Depends(get_db),
    ):
        return {"ok": True, "user_id": str(user.id)}

    @test_router.get("/test/sin-permiso")
    async def endpoint_sin_permiso(
        user=Depends(require_permission("no:existe")),
        db: AsyncSession = Depends(get_db),
    ):
        return {"ok": True}

    app.include_router(test_router)

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield {"client": client, "token": token, "tenant_id": tenant_a.id}


@pytest.mark.needs_db
class TestRequirePermission:
    async def test_con_permiso_pasa(self, rbac_client):
        c = rbac_client["client"]
        resp = await c.get(
            "/test/protegido",
            headers={
                "Authorization": f"Bearer {rbac_client['token']}",
                "X-Tenant-ID": str(rbac_client["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    async def test_sin_permiso_devuelve_403(self, rbac_client):
        c = rbac_client["client"]
        resp = await c.get(
            "/test/sin-permiso",
            headers={
                "Authorization": f"Bearer {rbac_client['token']}",
                "X-Tenant-ID": str(rbac_client["tenant_id"]),
            },
        )
        assert resp.status_code == 403
        assert "permiso" in resp.json()["detail"].lower()

    async def test_token_invalido_devuelve_401(self, rbac_client):
        c = rbac_client["client"]
        resp = await c.get(
            "/test/protegido",
            headers={
                "Authorization": "Bearer token-invalido",
                "X-Tenant-ID": str(rbac_client["tenant_id"]),
            },
        )
        assert resp.status_code == 401

    async def test_usuario_autenticado_sin_roles_devuelve_403(
        self, test_engine, tenant_a, db_session,
    ):
        settings = Settings()
        user = User(
            email="noroles@test.com",
            password_hash=hash_password("pass123!"),
            nombre="NoRoles", apellidos="",
            tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.commit()

        # Token JWT slim (sin roles)
        token = jwt.encode(
            {
                "sub": str(user.id),
                "tenant_id": str(tenant_a.id),
                "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            },
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

        from fastapi import APIRouter, Depends
        from app.core.dependencies import require_permission, get_db

        app = create_app()
        test_router = APIRouter()

        @test_router.get("/test/protegido")
        async def ep(
            user=Depends(require_permission("test:acceder")),
        ):
            return {"ok": True}

        app.include_router(test_router)

        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/test/protegido",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Tenant-ID": str(tenant_a.id),
                    },
                )
                assert resp.status_code == 403

    async def test_context_check_propio_ok(self, rbac_client):
        """Permiso (propio) con context_check que pasa."""
        from fastapi import APIRouter, Depends
        from app.core.dependencies import require_permission

        app = create_app()
        test_router = APIRouter()

        @test_router.get("/test/recurso-propio")
        async def recurso_propio(
            user=Depends(
                require_permission("test:acceder", context_check=lambda u: u.id == u.id)
            ),
        ):
            return {"ok": True, "user_id": str(user.id)}

        app.include_router(test_router)

        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/test/recurso-propio",
                    headers={
                        "Authorization": f"Bearer {rbac_client['token']}",
                        "X-Tenant-ID": str(rbac_client["tenant_id"]),
                    },
                )
                assert resp.status_code == 200
