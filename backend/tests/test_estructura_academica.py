"""Tests para estructura académica (C-06): Carrera, Cohorte, Materia."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import select

from app.core.config import Settings
from app.main import create_app
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
async def admin_estructura_client_and_data(test_engine, tenant_a, tenant_b, db_session):
    """Client with a seeded ADMIN user that has 'estructura:gestionar' permission."""
    settings = Settings()

    admin_rol = Rol(nombre="ADMIN_ESTRUCTURA", descripcion="Admin for tests", tenant_id=tenant_a.id)
    db_session.add(admin_rol)
    await db_session.flush()

    perm = Permiso(
        codigo="estructura:gestionar",
        descripcion="Gestionar estructura académica",
        modulo="estructura",
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
        email="admin_estructura@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="Estructura",
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

    # View-only user for 403 tests
    viewer_rol = Rol(nombre="VIEWER_EST", descripcion="Viewer", tenant_id=tenant_a.id)
    db_session.add(viewer_rol)
    await db_session.flush()

    viewer = User(
        email="viewer_est@test.com",
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
                "tenant_a_id": tenant_a.id,
                "tenant_b_id": tenant_b.id,
            }


# ── Carrera ───────────────────────────────────────────────────────────────


@pytest.mark.needs_db
class TestCarrera:
    async def test_admin_crea_carrera(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD", "nombre": "Tecnicatura en Programación", "activa": True},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["codigo"] == "TUPAD"
        assert data["nombre"] == "Tecnicatura en Programación"
        assert data["activa"] is True
        assert "id" in data

    async def test_admin_lista_carreras(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        # Create one first
        await c.post(
            "/api/admin/carreras",
            json={"codigo": "TUPA", "nombre": "Test", "activa": True},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        resp = await c.get(
            "/api/admin/carreras",
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_admin_actualiza_carrera(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "TUPAD2", "nombre": "Original", "activa": True},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        carrera_id = resp.json()["id"]

        resp = await c.put(
            f"/api/admin/carreras/{carrera_id}",
            json={"nombre": "Actualizado", "activa": False},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["nombre"] == "Actualizado"
        assert data["activa"] is False

    async def test_codigo_duplicado_409(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        await c.post(
            "/api/admin/carreras",
            json={"codigo": "DUPE", "nombre": "Original"},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "DUPE", "nombre": "Copia"},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 409

    async def test_sin_permiso_403(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "NO_PERM", "nombre": "Sin permiso"},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['viewer_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 403

    async def test_carrera_inexistente_404(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        fake_id = uuid.uuid4()
        resp = await c.put(
            f"/api/admin/carreras/{fake_id}",
            json={"nombre": "Nope"},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 404

    async def test_soft_delete_carrera(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "DEL_CAR", "nombre": "To Delete"},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        carrera_id = resp.json()["id"]

        resp = await c.delete(
            f"/api/admin/carreras/{carrera_id}",
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 200

        resp = await c.get(
            "/api/admin/carreras",
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        ids = [r["id"] for r in resp.json()]
        assert carrera_id not in ids


# ── Cohorte ───────────────────────────────────────────────────────────────


@pytest.mark.needs_db
class TestCohorte:
    async def _crear_carrera(self, client, token, tenant_id, codigo="CARR_COH"):
        resp = await client.post(
            "/api/admin/carreras",
            json={"codigo": codigo, "nombre": "Carrera Test", "activa": True},
            headers={
                "Authorization": f"Bearer {token}",
                "X-Tenant-ID": str(tenant_id),
            },
        )
        return resp.json()["id"]

    async def test_admin_crea_cohorte(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]
        carrera_id = await self._crear_carrera(c, token, t)

        resp = await c.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "MAR-2026",
                "anio": 2026,
                "vig_desde": "2026-03-01",
                "activa": True,
            },
            headers={
                "Authorization": f"Bearer {token}",
                "X-Tenant-ID": str(t),
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre"] == "MAR-2026"
        assert data["carrera_id"] == carrera_id
        assert data["activa"] is True

    async def test_cohorte_con_vig_hasta_null(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]
        carrera_id = await self._crear_carrera(c, token, t, "CARR_NULL")

        resp = await c.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "ABIERTA",
                "anio": 2026,
                "vig_desde": "2026-01-01",
                "activa": True,
            },
            headers={
                "Authorization": f"Bearer {token}",
                "X-Tenant-ID": str(t),
            },
        )
        assert resp.status_code == 201
        assert resp.json()["vig_hasta"] is None

    async def test_carrera_inactiva_rechaza_cohorte_activa_409(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "INACT", "nombre": "Inactiva", "activa": False},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        carrera_id = resp.json()["id"]

        resp = await c.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "NOPE",
                "anio": 2026,
                "vig_desde": "2026-01-01",
                "activa": True,
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 409

    async def test_cohorte_duplicado_409(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]
        carrera_id = await self._crear_carrera(c, token, t, "CARR_DUP")

        payload = {
            "carrera_id": carrera_id,
            "nombre": "UNICO",
            "anio": 2026,
            "vig_desde": "2026-01-01",
            "activa": True,
        }
        await c.post(
            "/api/admin/cohortes",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        resp = await c.post(
            "/api/admin/cohortes",
            json=payload,
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 409

    async def test_actualiza_cohorte(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]
        carrera_id = await self._crear_carrera(c, token, t, "CARR_UPD")

        resp = await c.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "INICIAL",
                "anio": 2026,
                "vig_desde": "2026-01-01",
                "activa": True,
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        cohorte_id = resp.json()["id"]

        resp = await c.put(
            f"/api/admin/cohortes/{cohorte_id}",
            json={"nombre": "ACTUALIZADA", "vig_hasta": "2026-08-31"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "ACTUALIZADA"
        assert resp.json()["vig_hasta"] == "2026-08-31"


# ── Materia ───────────────────────────────────────────────────────────────


@pytest.mark.needs_db
class TestMateria:
    async def test_admin_crea_materia(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        resp = await c.post(
            "/api/admin/materias",
            json={"codigo": "PROG_I", "nombre": "Programación I", "activa": True},
            headers={
                "Authorization": f"Bearer {admin_estructura_client_and_data['admin_token']}",
                "X-Tenant-ID": str(admin_estructura_client_and_data["tenant_a_id"]),
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["codigo"] == "PROG_I"
        assert data["activa"] is True

    async def test_materia_codigo_duplicado_409(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        await c.post(
            "/api/admin/materias",
            json={"codigo": "DUP_MAT", "nombre": "Original"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        resp = await c.post(
            "/api/admin/materias",
            json={"codigo": "DUP_MAT", "nombre": "Copia"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 409

    async def test_admin_lista_materias(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        await c.post(
            "/api/admin/materias",
            json={"codigo": "MAT_A", "nombre": "Materia A"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        resp = await c.get(
            "/api/admin/materias",
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    async def test_admin_actualiza_materia(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        resp = await c.post(
            "/api/admin/materias",
            json={"codigo": "MAT_UPD", "nombre": "Original", "activa": True},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        mat_id = resp.json()["id"]

        resp = await c.put(
            f"/api/admin/materias/{mat_id}",
            json={"nombre": "Actualizada", "activa": False},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Actualizada"
        assert resp.json()["activa"] is False


# ── Multi-tenant ──────────────────────────────────────────────────────────


@pytest.mark.needs_db
class TestMultiTenant:
    async def test_tenant_b_no_ve_carreras_de_tenant_a(
        self, admin_estructura_client_and_data, db_session, tenant_b,
    ):
        c = admin_estructura_client_and_data["client"]
        t_a = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        await c.post(
            "/api/admin/carreras",
            json={"codigo": "TENANT_A_ONLY", "nombre": "Solo A"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )

        # Crear un usuario admin en tenant_b para verificar aislamiento
        from app.models.rol import Rol as RolModel
        from app.models.permiso import Permiso as PermisoModel
        from app.models.rol_permiso import RolPermiso as RolPermisoModel
        from app.models.usuario_rol import UsuarioRol as UsuarioRolModel
        from app.models.user import User as UserModel
        from app.core.security import hash_password as hp

        admin_b_rol = RolModel(nombre="ADMIN_B", descripcion="Admin B", tenant_id=tenant_b.id)
        db_session.add(admin_b_rol)
        await db_session.flush()

        perm = await db_session.execute(
            select(PermisoModel).where(PermisoModel.codigo == "estructura:gestionar")
        )
        perm = perm.scalar_one()

        rp = RolPermisoModel(rol_id=admin_b_rol.id, permiso_id=perm.id, tenant_id=tenant_b.id)
        db_session.add(rp)

        user_b = UserModel(
            email="admin_b@test.com", password_hash=hp("pass123!"),
            nombre="Admin", apellidos="B", tenant_id=tenant_b.id,
        )
        db_session.add(user_b)
        await db_session.flush()

        ur = UsuarioRolModel(
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
            "/api/admin/carreras",
            headers={"Authorization": f"Bearer {token_b}", "X-Tenant-ID": str(tenant_b.id)},
        )
        codes = [r["codigo"] for r in resp.json()]
        assert "TENANT_A_ONLY" not in codes

    async def test_codigo_duplicado_entre_tenants_permitido(
        self, admin_estructura_client_and_data, db_session, tenant_b,
    ):
        c = admin_estructura_client_and_data["client"]
        t_a = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        await c.post(
            "/api/admin/carreras",
            json={"codigo": "MISMO_COD", "nombre": "Carrera en A"},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t_a)},
        )

        from app.models.rol import Rol as RolModel
        from app.models.permiso import Permiso as PermisoModel
        from app.models.rol_permiso import RolPermiso as RolPermisoModel
        from app.models.usuario_rol import UsuarioRol as UsuarioRolModel
        from app.models.user import User as UserModel
        from app.core.security import hash_password as hp

        admin_b_rol = RolModel(nombre="ADMIN_B2", descripcion="Admin B2", tenant_id=tenant_b.id)
        db_session.add(admin_b_rol)
        await db_session.flush()

        perm = await db_session.execute(
            select(PermisoModel).where(PermisoModel.codigo == "estructura:gestionar")
        )
        perm = perm.scalar_one()
        rp = RolPermisoModel(rol_id=admin_b_rol.id, permiso_id=perm.id, tenant_id=tenant_b.id)
        db_session.add(rp)

        user_b = UserModel(
            email="admin_b2@test.com", password_hash=hp("pass123!"),
            nombre="Admin", apellidos="B2", tenant_id=tenant_b.id,
        )
        db_session.add(user_b)
        await db_session.flush()
        ur = UsuarioRolModel(
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

        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "MISMO_COD", "nombre": "Carrera en B"},
            headers={"Authorization": f"Bearer {token_b}", "X-Tenant-ID": str(tenant_b.id)},
        )
        assert resp.status_code == 201


# ── Regla carrera inactiva ────────────────────────────────────────────────


@pytest.mark.needs_db
class TestReglaCarreraInactiva:
    async def test_inactivar_carrera_con_cohortes_activas_409(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "CON_COHORTES", "nombre": "Con cohortes activas", "activa": True},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        carrera_id = resp.json()["id"]

        await c.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "COH_ACT",
                "anio": 2026,
                "vig_desde": "2026-01-01",
                "activa": True,
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )

        resp = await c.put(
            f"/api/admin/carreras/{carrera_id}",
            json={"activa": False},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 409

    async def test_reactivar_cohorte_en_carrera_inactiva_409(self, admin_estructura_client_and_data):
        c = admin_estructura_client_and_data["client"]
        t = admin_estructura_client_and_data["tenant_a_id"]
        token = admin_estructura_client_and_data["admin_token"]

        # Create carrera inactive (no cohortes activas to block)
        resp = await c.post(
            "/api/admin/carreras",
            json={"codigo": "REACT_COH", "nombre": "React test", "activa": False},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        carrera_id = resp.json()["id"]

        # Create inactive cohorte (activa=False so it doesn't fail the carrera check)
        resp = await c.post(
            "/api/admin/cohortes",
            json={
                "carrera_id": carrera_id,
                "nombre": "COH_INACT",
                "anio": 2026,
                "vig_desde": "2026-01-01",
                "activa": False,
            },
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        cohorte_id = resp.json()["id"]

        # Try to reactivate the cohorte → 409 because carrera is inactive
        resp = await c.put(
            f"/api/admin/cohortes/{cohorte_id}",
            json={"activa": True},
            headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": str(t)},
        )
        assert resp.status_code == 409
