"""Tests para CRUD de roles y permisos (Grupo 5)."""

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
async def admin_client_and_data(test_engine, tenant_a, db_session):
    """Client with a seeded ADMIN user that has 'usuarios:gestionar' permission."""
    settings = Settings()

    admin_rol = Rol(nombre="ADMIN", descripcion="Admin", tenant_id=tenant_a.id)
    db_session.add(admin_rol)
    await db_session.flush()

    perm = Permiso(
        codigo="usuarios:gestionar",
        descripcion="Gestionar usuarios",
        modulo="usuarios",
    )
    db_session.add(perm)
    await db_session.flush()

    rp = RolPermiso(
        rol_id=admin_rol.id,
        permiso_id=perm.id,
        tenant_id=tenant_a.id,
    )
    db_session.add(rp)

    user = User(
        email="admin_crud@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="CRUD",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()

    ur = UsuarioRol(
        user_id=user.id,
        rol_id=admin_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)

    # Add a view-only user for 403 tests
    viewer_rol = Rol(nombre="VIEWER", descripcion="Viewer", tenant_id=tenant_a.id)
    db_session.add(viewer_rol)
    await db_session.flush()

    viewer = User(
        email="viewer@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Viewer", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(viewer)
    await db_session.flush()

    viewer_ur = UsuarioRol(
        user_id=viewer.id,
        rol_id=viewer_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(viewer_ur)
    await db_session.commit()

    admin_token = jwt.encode(
        {
            "sub": str(user.id),
            "tenant_id": str(tenant_a.id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        },
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    viewer_token = jwt.encode(
        {
            "sub": str(viewer.id),
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
                "admin_token": admin_token,
                "viewer_token": viewer_token,
                "tenant_id": tenant_a.id,
                "permiso_id": str(perm.id),
                "admin_rol_id": str(admin_rol.id),
            }


@pytest.mark.needs_db
class TestRolesCRUD:
    async def test_admin_lista_roles(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        resp = await c.get(
            "/api/v1/roles",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_viewer_no_puede_listar_roles(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        resp = await c.get(
            "/api/v1/roles",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['viewer_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 403

    async def test_admin_crea_rol(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        resp = await c.post(
            "/api/v1/roles",
            json={"nombre": "SUPERVISOR", "descripcion": "Supervisor de pruebas"},
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["nombre"] == "SUPERVISOR"

    async def test_admin_crea_rol_duplicado_falla(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        await c.post(
            "/api/v1/roles",
            json={"nombre": "DUPLICADO", "descripcion": "Original"},
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        resp = await c.post(
            "/api/v1/roles",
            json={"nombre": "DUPLICADO", "descripcion": "Copia"},
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 409

    async def test_admin_soft_delete_rol(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        # Create first
        resp = await c.post(
            "/api/v1/roles",
            json={"nombre": "ELIMINABLE", "descripcion": "To delete"},
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        rol_id = resp.json()["id"]

        # Delete
        resp = await c.delete(
            f"/api/v1/roles/{rol_id}",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 200

        # Verify it's gone from list
        resp = await c.get(
            "/api/v1/roles",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        names = [r["nombre"] for r in resp.json()]
        assert "ELIMINABLE" not in names


@pytest.mark.needs_db
class TestPermisosCRUD:
    async def test_admin_lista_permisos(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        resp = await c.get(
            "/api/v1/permisos",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_any_authenticated_user_can_list_permisos(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        resp = await c.get(
            "/api/v1/permisos",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['viewer_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 200

    async def test_admin_asigna_permiso_a_rol(self, admin_client_and_data, db_session):
        # Use a different permiso that isn't already assigned
        from app.models.permiso import Permiso as PermisoModel
        otro_permiso = PermisoModel(
            codigo="test:nueva_asignacion",
            descripcion="Nuevo permiso para test",
            modulo="test",
        )
        db_session.add(otro_permiso)
        await db_session.commit()

        c = admin_client_and_data["client"]
        rol_id = admin_client_and_data["admin_rol_id"]
        resp = await c.post(
            f"/api/v1/roles/{rol_id}/permisos",
            json={"permiso_id": str(otro_permiso.id)},
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 200

    async def test_admin_quita_permiso_de_rol(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        rol_id = admin_client_and_data["admin_rol_id"]
        permiso_id = admin_client_and_data["permiso_id"]

        resp = await c.delete(
            f"/api/v1/roles/{rol_id}/permisos/{permiso_id}",
            headers={
                "Authorization": f"Bearer {admin_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 200

    async def test_viewer_no_puede_asignar_permiso(self, admin_client_and_data, db_session):
        from app.models.permiso import Permiso as PermisoModel
        otro = PermisoModel(
            codigo="test:viewer_no_assign",
            descripcion="Para test viewer",
            modulo="test",
        )
        db_session.add(otro)
        await db_session.commit()

        c = admin_client_and_data["client"]
        rol_id = admin_client_and_data["admin_rol_id"]
        resp = await c.post(
            f"/api/v1/roles/{rol_id}/permisos",
            json={"permiso_id": str(otro.id)},
            headers={
                "Authorization": f"Bearer {admin_client_and_data['viewer_token']}",
                "X-Tenant-ID": str(admin_client_and_data["tenant_id"]),
            },
        )
        assert resp.status_code == 403
