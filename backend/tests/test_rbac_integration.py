"""Tests de integración RBAC (Grupo 6)."""

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
async def multi_tenant_setup(test_engine, tenant_a, tenant_b, db_session):
    """Two tenants with their own roles."""
    settings = Settings()

    # Tenant A: rol ADMIN with usuarios:gestionar
    rol_a = Rol(nombre="ADMIN", descripcion="Admin A", tenant_id=tenant_a.id)
    db_session.add(rol_a)
    perm = Permiso(codigo="usuarios:gestionar", descripcion="Gestionar usuarios", modulo="usuarios")
    db_session.add(perm)
    await db_session.flush()
    db_session.add(RolPermiso(rol_id=rol_a.id, permiso_id=perm.id, tenant_id=tenant_a.id))

    # Tenant B: rol ADMIN without usuarios:gestionar
    rol_b = Rol(nombre="ADMIN", descripcion="Admin B", tenant_id=tenant_b.id)
    db_session.add(rol_b)

    user_a = User(
        email="admin_a@test.com", password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="A", tenant_id=tenant_a.id,
    )
    db_session.add(user_a)
    user_b = User(
        email="admin_b@test.com", password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="B", tenant_id=tenant_b.id,
    )
    db_session.add(user_b)
    await db_session.flush()

    ahora = datetime.now(timezone.utc) - timedelta(days=30)
    db_session.add(UsuarioRol(user_id=user_a.id, rol_id=rol_a.id, fecha_desde=ahora, tenant_id=tenant_a.id))
    db_session.add(UsuarioRol(user_id=user_b.id, rol_id=rol_b.id, fecha_desde=ahora, tenant_id=tenant_b.id))
    await db_session.commit()

    token_a = jwt.encode({"sub": str(user_a.id), "tenant_id": str(tenant_a.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, settings.secret_key, algorithm=settings.jwt_algorithm)
    token_b = jwt.encode({"sub": str(user_b.id), "tenant_id": str(tenant_b.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, settings.secret_key, algorithm=settings.jwt_algorithm)

    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield {
                "client": c,
                "token_a": token_a,
                "token_b": token_b,
                "tenant_a": tenant_a.id,
                "tenant_b": tenant_b.id,
            }


@pytest.mark.needs_db
class TestIntegration:
    async def test_tenant_isolation_roles(self, multi_tenant_setup):
        """6.5: Tenant A no ve roles del Tenant B."""
        c = multi_tenant_setup["client"]

        # Tenant A crea un rol
        await c.post(
            "/api/v1/roles",
            json={"nombre": "ROL_SECRETO", "descripcion": "Solo A"},
            headers={
                "Authorization": f"Bearer {multi_tenant_setup['token_a']}",
                "X-Tenant-ID": str(multi_tenant_setup["tenant_a"]),
            },
        )

        # Tenant B no debería verlo
        resp = await c.get(
            "/api/v1/roles",
            headers={
                "Authorization": f"Bearer {multi_tenant_setup['token_b']}",
                "X-Tenant-ID": str(multi_tenant_setup["tenant_b"]),
            },
        )
        # Tenant B no tiene usuarios:gestionar → 403
        assert resp.status_code == 403

    async def test_union_roles_integration(self, test_engine, tenant_a, db_session):
        """6.2: Unión de roles funciona en endpoint real."""
        settings = Settings()

        # Crear roles y permisos
        profe = Rol(nombre="PROFESOR", descripcion="Teacher", tenant_id=tenant_a.id)
        coord = Rol(nombre="COORDINADOR", descripcion="Coordinator", tenant_id=tenant_a.id)
        db_session.add(profe)
        db_session.add(coord)
        await db_session.flush()

        for codigo, modulo in [("calificaciones:importar", "calificaciones"), ("comunicacion:enviar", "comunicacion")]:
            p = Permiso(codigo=codigo, descripcion=codigo, modulo=modulo)
            db_session.add(p)
            await db_session.flush()
            if codigo == "calificaciones:importar":
                db_session.add(RolPermiso(rol_id=profe.id, permiso_id=p.id, tenant_id=tenant_a.id))
            else:
                db_session.add(RolPermiso(rol_id=coord.id, permiso_id=p.id, tenant_id=tenant_a.id))

        user = User(
            email="union@test.com", password_hash=hash_password("pass123!"),
            nombre="Union", apellidos="", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()

        ahora = datetime.now(timezone.utc) - timedelta(days=30)
        db_session.add(UsuarioRol(user_id=user.id, rol_id=profe.id, fecha_desde=ahora, tenant_id=tenant_a.id))
        db_session.add(UsuarioRol(user_id=user.id, rol_id=coord.id, fecha_desde=ahora, tenant_id=tenant_a.id))
        await db_session.commit()

        token = jwt.encode({"sub": str(user.id), "tenant_id": str(tenant_a.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, settings.secret_key, algorithm=settings.jwt_algorithm)

        # Create a protected endpoint
        from fastapi import APIRouter, Depends
        from app.core.dependencies import require_permission

        app = create_app()
        test_router = APIRouter()

        @test_router.get("/test/check-cali")
        async def check_cali(user=Depends(require_permission("calificaciones:importar"))):
            return {"ok": True}

        @test_router.get("/test/check-com")
        async def check_com(user=Depends(require_permission("comunicacion:enviar"))):
            return {"ok": True}

        app.include_router(test_router)

        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get("/test/check-cali", headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_a.id)})
                assert resp.status_code == 200

                resp = await c.get("/test/check-com", headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_a.id)})
                assert resp.status_code == 200

    async def test_sin_permiso_en_endpoint_protegido(self, test_engine, tenant_a, db_session):
        """6.1: Usuario sin permiso recibe 403 en endpoint protegido."""
        settings = Settings()

        user = User(
            email="sinpermiso@test.com", password_hash=hash_password("pass123!"),
            nombre="SinPermiso", apellidos="", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.commit()

        token = jwt.encode({"sub": str(user.id), "tenant_id": str(tenant_a.id), "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, settings.secret_key, algorithm=settings.jwt_algorithm)

        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/v1/roles",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-Tenant-ID": str(tenant_a.id),
                    },
                )
                assert resp.status_code == 403
