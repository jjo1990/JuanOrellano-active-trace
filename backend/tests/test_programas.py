"""Tests para programas de materia (C-17): CRUD, tenancy, permisos."""

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
from app.models.usuario_rol import UsuarioRol
from app.models.user import User


@pytest.fixture
async def admin_client_and_data(test_engine, tenant_a, tenant_b, db_session):
    settings = Settings()

    admin_rol = Rol(nombre="ADMIN_PROG", descripcion="Admin for tests", tenant_id=tenant_a.id)
    db_session.add(admin_rol)
    await db_session.flush()

    perm = Permiso(
        codigo="estructura:gestionar",
        descripcion="Gestionar estructura academica",
        modulo="estructura",
    )
    db_session.add(perm)
    await db_session.flush()

    rp = RolPermiso(rol_id=admin_rol.id, permiso_id=perm.id, tenant_id=tenant_a.id)
    db_session.add(rp)

    user = User(
        email="admin_prog@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="Programas",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()

    ur = UsuarioRol(
        user_id=user.id, rol_id=admin_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)

    viewer_rol = Rol(nombre="VIEWER_PROG", descripcion="Viewer", tenant_id=tenant_a.id)
    db_session.add(viewer_rol)
    await db_session.flush()

    viewer = User(
        email="viewer_prog@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Viewer", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(viewer)
    await db_session.flush()

    viewer_ur = UsuarioRol(
        user_id=viewer.id, rol_id=viewer_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(viewer_ur)
    await db_session.commit()

    admin_token = jwt.encode(
        {"sub": str(user.id), "tenant_id": str(tenant_a.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )
    viewer_token = jwt.encode(
        {"sub": str(viewer.id), "tenant_id": str(tenant_a.id),
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
                "viewer_token": viewer_token,
                "tenant_a_id": tenant_a.id,
                "tenant_b_id": tenant_b.id,
            }


async def _setup_entities(client, token, tenant_id):
    """Create carrera, cohorte, materia for FK references."""
    resp = await client.post(
        "/api/admin/carreras",
        json={"codigo": "PROG_CARR", "nombre": "Carrera Prog", "activa": True},
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_id)},
    )
    carrera_id = resp.json()["id"]

    resp = await client.post(
        "/api/admin/cohortes",
        json={
            "carrera_id": carrera_id, "nombre": "COH_PROG", "anio": 2026,
            "vig_desde": "2026-01-01", "activa": True,
        },
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_id)},
    )
    cohorte_id = resp.json()["id"]

    resp = await client.post(
        "/api/admin/materias",
        json={"codigo": "MAT_PROG", "nombre": "Materia Prog", "activa": True},
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_id)},
    )
    materia_id = resp.json()["id"]

    return carrera_id, cohorte_id, materia_id


@pytest.mark.needs_db
class TestPrograma:
    async def test_crea_programa(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        resp = await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id,
                "carrera_id": carrera_id,
                "cohorte_id": cohorte_id,
                "titulo": "Programa de Programacion I",
                "referencia_archivo": "s3://activia-trace/programas/prog_i.pdf",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["titulo"] == "Programa de Programacion I"
        assert data["referencia_archivo"] == "s3://activia-trace/programas/prog_i.pdf"
        assert data["materia_id"] == materia_id
        assert data["carrera_id"] == carrera_id
        assert data["cohorte_id"] == cohorte_id
        assert "cargado_at" in data
        assert "id" in data

    async def test_crea_programa_sin_referencia_archivo_422(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        resp = await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id,
                "carrera_id": carrera_id,
                "cohorte_id": cohorte_id,
                "titulo": "Sin archivo",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 422

    async def test_lista_programas_con_filtro(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id, "carrera_id": carrera_id,
                "cohorte_id": cohorte_id, "titulo": "Programa A",
                "referencia_archivo": "s3://a.pdf",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )

        resp = await c.get(
            f"/api/programas?materia_id={materia_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["titulo"] == "Programa A"

    async def test_get_programa_detail(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        resp = await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id, "carrera_id": carrera_id,
                "cohorte_id": cohorte_id, "titulo": "Detalle",
                "referencia_archivo": "s3://detalle.pdf",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        prog_id = resp.json()["id"]

        resp = await c.get(
            f"/api/programas/{prog_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        assert resp.json()["titulo"] == "Detalle"

    async def test_get_programa_inexistente_404(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        fake_id = uuid.uuid4()

        resp = await c.get(
            f"/api/programas/{fake_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 404

    async def test_update_programa(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        resp = await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id, "carrera_id": carrera_id,
                "cohorte_id": cohorte_id, "titulo": "Original",
                "referencia_archivo": "s3://old.pdf",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        prog_id = resp.json()["id"]

        resp = await c.put(
            f"/api/programas/{prog_id}",
            json={"titulo": "Actualizado", "referencia_archivo": "s3://new.pdf"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["titulo"] == "Actualizado"
        assert data["referencia_archivo"] == "s3://new.pdf"

    async def test_soft_delete_programa(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        resp = await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id, "carrera_id": carrera_id,
                "cohorte_id": cohorte_id, "titulo": "To Delete",
                "referencia_archivo": "s3://del.pdf",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        prog_id = resp.json()["id"]

        resp = await c.delete(
            f"/api/programas/{prog_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200

        resp = await c.get(
            "/api/programas",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        ids = [r["id"] for r in resp.json()]
        assert prog_id not in ids

    async def test_sin_permiso_403(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        viewer_token = admin_client_and_data["viewer_token"]
        carrera_id, cohorte_id, materia_id = await _setup_entities(c, token, t)

        resp = await c.post(
            "/api/programas",
            json={
                "materia_id": materia_id, "carrera_id": carrera_id,
                "cohorte_id": cohorte_id, "titulo": "No perm",
                "referencia_archivo": "s3://nope.pdf",
            },
            headers={"Authorization": f"Bearer {viewer_token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 403

    async def test_delete_inexistente_404(self, admin_client_and_data):
        c = admin_client_and_data["client"]
        t = admin_client_and_data["tenant_a_id"]
        token = admin_client_and_data["admin_token"]
        fake_id = uuid.uuid4()

        resp = await c.delete(
            f"/api/programas/{fake_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 404
