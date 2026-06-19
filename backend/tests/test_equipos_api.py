import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import Settings
from app.core.database import create_engine, Base
from app.core.security import hash_password
from app.main import create_app
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user import User
from app.models.usuario_rol import UsuarioRol


@pytest.fixture
async def api_seed(test_engine, tenant_a):
    from sqlalchemy.ext.asyncio import async_sessionmaker

    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as db_session:
        settings = Settings()

        # Roles
        profe_rol = Rol(nombre="PROFESOR_API", descripcion="Prof API", tenant_id=tenant_a.id)
        coord_rol = Rol(nombre="COORDINADOR_API", descripcion="Coord API", tenant_id=tenant_a.id)
        tutor_rol = Rol(nombre="TUTOR_API", descripcion="Tutor API", tenant_id=tenant_a.id)
        db_session.add_all([profe_rol, coord_rol, tutor_rol])
        await db_session.flush()

        # Permissions
        from sqlalchemy import select

        perm_ver_propio = Permiso(
            codigo="equipos:ver_propio", descripcion="Ver propio", modulo="equipos",
        )
        db_session.add(perm_ver_propio)
        await db_session.flush()

        db_session.add(RolPermiso(rol_id=profe_rol.id, permiso_id=perm_ver_propio.id, tenant_id=tenant_a.id))
        db_session.add(RolPermiso(rol_id=tutor_rol.id, permiso_id=perm_ver_propio.id, tenant_id=tenant_a.id))
        db_session.add(RolPermiso(rol_id=coord_rol.id, permiso_id=perm_ver_propio.id, tenant_id=tenant_a.id))
        await db_session.flush()

        perm_asignar = await db_session.execute(
            select(Permiso).where(Permiso.codigo == "equipos:asignar")
        )
        perm_asignar = perm_asignar.scalar_one_or_none()
        if perm_asignar is None:
            perm_asignar = Permiso(
                codigo="equipos:asignar", descripcion="Asignar", modulo="equipos",
            )
            db_session.add(perm_asignar)
            await db_session.flush()

        db_session.add(RolPermiso(rol_id=coord_rol.id, permiso_id=perm_asignar.id, tenant_id=tenant_a.id))
        await db_session.flush()

        # Users
        profe_user = User(
            email="profe_api@test.com", password_hash=hash_password("pass123!"),
            nombre="Juan", apellidos="Profesor", legajo="L-001", tenant_id=tenant_a.id,
        )
        coord_user = User(
            email="coord_api@test.com", password_hash=hash_password("pass123!"),
            nombre="Ana", apellidos="Coordinadora", legajo="L-002", tenant_id=tenant_a.id,
        )
        tutor_user = User(
            email="tutor_api@test.com", password_hash=hash_password("pass123!"),
            nombre="Maria", apellidos="Tutora", legajo="L-003", tenant_id=tenant_a.id,
        )
        db_session.add_all([profe_user, coord_user, tutor_user])
        await db_session.flush()

        db_session.add(UsuarioRol(
            user_id=profe_user.id, rol_id=profe_rol.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30), tenant_id=tenant_a.id,
        ))
        db_session.add(UsuarioRol(
            user_id=coord_user.id, rol_id=coord_rol.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30), tenant_id=tenant_a.id,
        ))
        db_session.add(UsuarioRol(
            user_id=tutor_user.id, rol_id=tutor_rol.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30), tenant_id=tenant_a.id,
        ))
        await db_session.flush()

        # Academic entities
        materia = Materia(codigo="MAT_API", nombre="Matematica API", activa=True, tenant_id=tenant_a.id)
        db_session.add(materia)
        await db_session.flush()

        carrera = Carrera(codigo="CAR_API", nombre="Ingenieria API", activa=True, tenant_id=tenant_a.id)
        db_session.add(carrera)
        await db_session.flush()

        cohorte = Cohorte(
            carrera_id=carrera.id, nombre="2026-API", anio=2026,
            vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
        )
        cohorte_dest = Cohorte(
            carrera_id=carrera.id, nombre="2026-API-DEST", anio=2026,
            vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
        )
        db_session.add_all([cohorte, cohorte_dest])
        await db_session.flush()

        # Assign profe to a materia
        asig = Asignacion(
            usuario_id=profe_user.id, rol_id=profe_rol.id,
            materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
            comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
            tenant_id=tenant_a.id,
        )
        db_session.add(asig)
        await db_session.commit()

        exp = datetime.now(timezone.utc) + timedelta(minutes=15)
        profe_token = jwt.encode(
            {"sub": str(profe_user.id), "tenant_id": str(tenant_a.id), "exp": exp},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )
        coord_token = jwt.encode(
            {"sub": str(coord_user.id), "tenant_id": str(tenant_a.id), "exp": exp},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )
        tutor_token = jwt.encode(
            {"sub": str(tutor_user.id), "tenant_id": str(tenant_a.id), "exp": exp},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )

        return {
            "tenant_a_id": tenant_a.id,
            "profe_token": profe_token,
            "coord_token": coord_token,
            "tutor_token": tutor_token,
            "profe_user_id": profe_user.id,
            "coord_user_id": coord_user.id,
            "tutor_user_id": tutor_user.id,
            "profe_rol_id": profe_rol.id,
            "coord_rol_id": coord_rol.id,
            "tutor_rol_id": tutor_rol.id,
            "materia_id": materia.id,
            "carrera_id": carrera.id,
            "cohorte_id": cohorte.id,
            "cohorte_dest_id": cohorte_dest.id,
        }


@pytest.mark.needs_db
class TestMisEquiposAPI:
    async def test_returns_200_with_enriched_data(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/equipos/mis-equipos",
                    headers={
                        "Authorization": f"Bearer {d['profe_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 200
                data = resp.json()
                assert isinstance(data, list)
                assert len(data) >= 1
                item = data[0]
                assert "usuario_nombre" in item
                assert "rol_nombre" in item
                assert "materia_nombre" in item
                assert "estado_vigencia" in item

    async def test_returns_401_without_auth(self, api_seed):
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get("/api/equipos/mis-equipos")
                assert resp.status_code in (401, 403)

    async def test_returns_200_with_combined_filters(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    f"/api/equipos/mis-equipos?vigente=true&materia_id={d['materia_id']}&rol_id={d['profe_rol_id']}",
                    headers={
                        "Authorization": f"Bearer {d['profe_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 200


@pytest.mark.needs_db
class TestAsignacionMasivaAPI:
    async def test_creates_assignments_returns_201(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.post(
                    "/api/equipos/asignacion-masiva",
                    json={
                        "usuarios": [{"id": str(d["cohorte_id"])}],
                        "materia_id": str(d["materia_id"]),
                        "rol_id": str(d["profe_rol_id"]),
                        "desde": "2026-08-01",
                        "hasta": "2026-12-31",
                    },
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                # Invalid user = best-effort creates 0 success
                assert resp.status_code == 201

    async def test_with_valid_users_returns_201(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.post(
                    "/api/equipos/asignacion-masiva",
                    json={
                        "usuarios": [
                            {"id": str(d["profe_user_id"])},
                            {"id": str(d["tutor_user_id"])},
                        ],
                        "materia_id": str(d["materia_id"]),
                        "rol_id": str(d["profe_rol_id"]),
                        "desde": "2026-08-01",
                        "hasta": "2026-12-31",
                    },
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 201
                data = resp.json()
                assert data["total_exitosos"] == 2
                assert data["total_fallidos"] == 0

    async def test_without_permission_returns_403(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.post(
                    "/api/equipos/asignacion-masiva",
                    json={
                        "usuarios": [{"id": str(d["profe_user_id"])}],
                        "rol_id": str(d["profe_rol_id"]),
                        "desde": "2026-08-01",
                    },
                    headers={
                        "Authorization": f"Bearer {d['profe_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 403

    async def test_invalid_dates_returns_422(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.post(
                    "/api/equipos/asignacion-masiva",
                    json={
                        "usuarios": [{"id": str(d["profe_user_id"])}],
                        "rol_id": str(d["profe_rol_id"]),
                        "desde": "2026-12-31",
                        "hasta": "2026-01-01",
                    },
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 422


@pytest.mark.needs_db
class TestClonarEquipoAPI:
    async def test_clones_returns_201(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.post(
                    "/api/equipos/clonar",
                    json={
                        "materia_id": str(d["materia_id"]),
                        "carrera_id": str(d["carrera_id"]),
                        "cohorte_origen_id": str(d["cohorte_id"]),
                        "cohorte_destino_id": str(d["cohorte_dest_id"]),
                        "desde": "2027-01-01",
                        "hasta": "2027-12-31",
                    },
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 201
                data = resp.json()
                assert data["total_clonadas"] >= 1

    async def test_same_origin_destino_returns_422(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.post(
                    "/api/equipos/clonar",
                    json={
                        "materia_id": str(d["materia_id"]),
                        "carrera_id": str(d["carrera_id"]),
                        "cohorte_origen_id": str(d["cohorte_id"]),
                        "cohorte_destino_id": str(d["cohorte_id"]),
                        "desde": "2027-01-01",
                    },
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 422


@pytest.mark.needs_db
class TestVigenciaAPI:
    async def test_returns_200(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.put(
                    "/api/equipos/vigencia",
                    json={
                        "materia_id": str(d["materia_id"]),
                        "desde": "2027-01-01",
                    },
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 200
                data = resp.json()
                assert "asignaciones_actualizadas" in data
                assert "total_encontradas" in data

    async def test_no_filters_returns_422(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.put(
                    "/api/equipos/vigencia",
                    json={"desde": "2027-01-01"},
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 422


@pytest.mark.needs_db
class TestExportarAPI:
    async def test_returns_csv_200(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/equipos/exportar",
                    params={"materia_id": str(d["materia_id"])},
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 200
                assert "text/csv" in resp.headers.get("content-type", "")

    async def test_no_filters_returns_400(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/equipos/exportar",
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 400


@pytest.mark.needs_db
class TestBuscarUsuariosAPI:
    async def test_returns_200_with_results(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/equipos/buscar-usuarios",
                    params={"q": "juan"},
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 200
                data = resp.json()
                assert isinstance(data, list)
                assert any("Juan" in r.get("nombre", "") for r in data)

    async def test_empty_query_returns_200_empty(self, api_seed):
        d = api_seed
        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/equipos/buscar-usuarios",
                    params={"q": ""},
                    headers={
                        "Authorization": f"Bearer {d['coord_token']}",
                        "X-Tenant-ID": str(d["tenant_a_id"]),
                    },
                )
                assert resp.status_code == 200
                assert resp.json() == []
