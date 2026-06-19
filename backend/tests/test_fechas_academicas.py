"""Tests for fechas academicas (C-17): CRUD, calendario, cronograma, tenancy, permisos."""

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
async def admin_fechas_client_and_data(test_engine, tenant_a, tenant_b, db_session):
    settings = Settings()

    admin_rol = Rol(nombre="ADMIN_FECHAS", descripcion="Admin for tests", tenant_id=tenant_a.id)
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
        email="admin_fechas@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="Fechas",
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

    viewer_rol = Rol(nombre="VIEWER_FECHAS", descripcion="Viewer", tenant_id=tenant_a.id)
    db_session.add(viewer_rol)
    await db_session.flush()

    viewer = User(
        email="viewer_fechas@test.com",
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


async def _setup_fechas_entities(client, token, tenant_id):
    resp = await client.post(
        "/api/admin/carreras",
        json={"codigo": "FECH_CARR", "nombre": "Carrera Fechas", "activa": True},
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_id)},
    )
    carrera_id = resp.json()["id"]

    resp = await client.post(
        "/api/admin/cohortes",
        json={
            "carrera_id": carrera_id, "nombre": "COH_FECH", "anio": 2026,
            "vig_desde": "2026-01-01", "activa": True,
        },
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_id)},
    )
    cohorte_id = resp.json()["id"]

    resp = await client.post(
        "/api/admin/materias",
        json={"codigo": "MAT_FECH", "nombre": "Materia Fechas", "activa": True},
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tenant_id)},
    )
    materia_id = resp.json()["id"]

    return carrera_id, cohorte_id, materia_id


@pytest.mark.needs_db
class TestFechaAcademica:
    async def test_crea_fecha_parcial(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        resp = await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id,
                "cohorte_id": cohorte_id,
                "tipo": "Parcial",
                "numero": 1,
                "periodo": "Abril 2026",
                "fecha": "2026-04-15",
                "titulo": "Primer Parcial",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["tipo"] == "Parcial"
        assert data["numero"] == 1
        assert data["fecha"] == "2026-04-15"
        assert data["titulo"] == "Primer Parcial"
        assert data["id"] is not None

    async def test_crea_fecha_coloquio(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        resp = await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id,
                "cohorte_id": cohorte_id,
                "tipo": "Coloquio",
                "numero": 1,
                "periodo": "Junio 2026",
                "fecha": "2026-06-15",
                "titulo": "Coloquio Final",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 201
        assert resp.json()["tipo"] == "Coloquio"

    async def test_lista_fechas_con_filtro(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 1, "periodo": "Abril 2026",
                "fecha": "2026-04-15", "titulo": "Parcial 1",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "TP", "numero": 1, "periodo": "Mayo 2026",
                "fecha": "2026-05-10", "titulo": "TP 1",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )

        resp = await c.get(
            f"/api/fechas-academicas?cohorte_id={cohorte_id}&tipo=Parcial",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["tipo"] == "Parcial"

    async def test_calendario_agrupado(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 1, "periodo": "Marzo 2026",
                "fecha": "2026-03-15", "titulo": "Parcial Marzo",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 2, "periodo": "Abril 2026",
                "fecha": "2026-04-20", "titulo": "Parcial Abril",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )

        resp = await c.get(
            f"/api/fechas-academicas/calendario?cohorte_id={cohorte_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "calendario" in data
        assert "2026-03" in data["calendario"]
        assert "2026-04" in data["calendario"]
        assert len(data["calendario"]["2026-03"]) == 1
        assert len(data["calendario"]["2026-04"]) == 1

    async def test_cronograma_lms_html(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 1, "periodo": "Abril 2026",
                "fecha": "2026-04-15", "titulo": "Parcial 1",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )

        resp = await c.get(
            f"/api/fechas-academicas/cronograma-lms?materia_id={materia_id}&cohorte_id={cohorte_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "html" in data
        assert "<table>" in data["html"]
        assert "Parcial 1" in data["html"]
        assert "2026-04-15" in data["html"]

    async def test_update_fecha(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        resp = await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 1, "periodo": "Abril 2026",
                "fecha": "2026-04-15", "titulo": "Original",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        fecha_id = resp.json()["id"]

        resp = await c.put(
            f"/api/fechas-academicas/{fecha_id}",
            json={"titulo": "Modificado", "fecha": "2026-04-20"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["titulo"] == "Modificado"
        assert data["fecha"] == "2026-04-20"

    async def test_soft_delete_fecha(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        resp = await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "TP", "numero": 1, "periodo": "Mayo 2026",
                "fecha": "2026-05-10", "titulo": "To Delete",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        fecha_id = resp.json()["id"]

        resp = await c.delete(
            f"/api/fechas-academicas/{fecha_id}",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200

        resp = await c.get(
            "/api/fechas-academicas",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        ids = [r["id"] for r in resp.json()]
        assert fecha_id not in ids

    async def test_sin_permiso_403(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        viewer_token = admin_fechas_client_and_data["viewer_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t)

        resp = await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 1, "periodo": "Abril 2026",
                "fecha": "2026-04-15", "titulo": "No perm",
            },
            headers={"Authorization": f"Bearer {viewer_token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 403

    async def test_fecha_inexistente_404(self, admin_fechas_client_and_data):
        c = admin_fechas_client_and_data["client"]
        t = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        fake_id = uuid.uuid4()

        resp = await c.put(
            f"/api/fechas-academicas/{fake_id}",
            json={"titulo": "Nope"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 404


@pytest.mark.needs_db
class TestFechasMultiTenant:
    async def test_tenant_b_no_ve_fechas_de_tenant_a(
        self, admin_fechas_client_and_data, db_session, tenant_b,
    ):
        c = admin_fechas_client_and_data["client"]
        t_a = admin_fechas_client_and_data["tenant_a_id"]
        token = admin_fechas_client_and_data["admin_token"]
        _carr, cohorte_id, materia_id = await _setup_fechas_entities(c, token, t_a)

        await c.post(
            "/api/fechas-academicas",
            json={
                "materia_id": materia_id, "cohorte_id": cohorte_id,
                "tipo": "Parcial", "numero": 1, "periodo": "Abril 2026",
                "fecha": "2026-04-15", "titulo": "Solo A",
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )

        admin_b_rol = Rol(nombre="ADMIN_FECH_B", descripcion="Admin B", tenant_id=tenant_b.id)
        db_session.add(admin_b_rol)
        await db_session.flush()

        perm = await db_session.execute(
            select(Permiso).where(Permiso.codigo == "estructura:gestionar")
        )
        perm = perm.scalar_one()
        rp = RolPermiso(rol_id=admin_b_rol.id, permiso_id=perm.id, tenant_id=tenant_b.id)
        db_session.add(rp)

        user_b = User(
            email="admin_fech_b@test.com", password_hash=hash_password("pass123!"),
            nombre="Admin", apellidos="B", tenant_id=tenant_b.id,
        )
        db_session.add(user_b)
        await db_session.flush()
        ur = UsuarioRol(
            user_id=user_b.id, rol_id=admin_b_rol.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
            tenant_id=tenant_b.id,
        )
        db_session.add(ur)
        await db_session.commit()

        settings = Settings()
        token_b = jwt.encode(
            {"sub": str(user_b.id), "tenant_id": str(tenant_b.id),
             "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )

        resp = await c.get(
            "/api/fechas-academicas",
            headers={"Authorization": f"Bearer {token_b}", "X-Tenant-ID": str(tenant_b.id)},
        )
        titulos = [r["titulo"] for r in resp.json()]
        assert "Solo A" not in titulos
