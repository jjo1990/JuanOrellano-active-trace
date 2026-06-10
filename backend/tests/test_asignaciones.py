"""Tests para C-07 asignaciones: CRUD, vigencia, multi-rol, filtros, tenancy."""

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.config import Settings
from app.core.database import create_engine
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
from app.services.asignacion_service import AsignacionService


@pytest.fixture
async def setup_equipos_data(test_engine, tenant_a, tenant_b, db_session):
    """Seed roles, permissions, and entities for equipo tests."""
    settings = Settings()

    # Seed roles + permisos
    admin_rol = Rol(nombre="ADMIN_EQUIPOS", descripcion="Admin", tenant_id=tenant_a.id)
    db_session.add(admin_rol)
    profe_rol = Rol(nombre="PROFESOR_EQUIPOS", descripcion="Prof", tenant_id=tenant_a.id)
    db_session.add(profe_rol)
    coord_rol = Rol(nombre="COORD_EQUIPOS", descripcion="Coord", tenant_id=tenant_a.id)
    db_session.add(coord_rol)
    await db_session.flush()

    perm_asignar = Permiso(codigo="equipos:asignar", descripcion="Asignar", modulo="equipos")
    db_session.add(perm_asignar)
    perm_profe = Permiso(codigo="calificaciones:importar", descripcion="Importar calis", modulo="calificaciones")
    db_session.add(perm_profe)
    perm_coord = Permiso(codigo="comunicacion:enviar", descripcion="Enviar coms", modulo="comunicacion")
    db_session.add(perm_coord)
    await db_session.flush()

    db_session.add(RolPermiso(rol_id=admin_rol.id, permiso_id=perm_asignar.id, tenant_id=tenant_a.id))
    db_session.add(RolPermiso(rol_id=profe_rol.id, permiso_id=perm_profe.id, tenant_id=tenant_a.id))
    db_session.add(RolPermiso(rol_id=coord_rol.id, permiso_id=perm_coord.id, tenant_id=tenant_a.id))
    await db_session.flush()

    # Admin user
    admin_user = User(
        email="admin_eq@test.com", password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="Equipos", tenant_id=tenant_a.id,
    )
    db_session.add(admin_user)
    await db_session.flush()
    db_session.add(UsuarioRol(
        user_id=admin_user.id, rol_id=admin_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    ))

    admin_token = jwt.encode(
        {"sub": str(admin_user.id), "tenant_id": str(tenant_a.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )

    # Materia, Carrera for FKs
    materia = Materia(codigo="MAT_ASIG", nombre="Materia Asignacion", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()
    carrera = Carrera(codigo="CAR_ASIG", nombre="Carrera Asignacion", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="COH_ASIG", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.commit()

    return {
        "admin_token": admin_token,
        "tenant_a_id": tenant_a.id,
        "tenant_b_id": tenant_b.id,
        "admin_user_id": admin_user.id,
        "profe_rol_id": profe_rol.id,
        "coord_rol_id": coord_rol.id,
        "admin_rol_id": admin_rol.id,
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
    }


def _make_client():
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test"), app


@pytest.mark.needs_db
class TestAsignacionCRUD:
    """9.5: CRUD asignaciones."""

    async def test_create_list_get_update_delete(self, setup_equipos_data, db_session, tenant_a):
        settings = Settings()
        d = setup_equipos_data
        client, app = _make_client()

        # Create a target user for the asignacion
        target_user = User(
            email="target_asig@test.com", password_hash="hash",
            nombre="Target", apellidos="Asig", tenant_id=d["tenant_a_id"],
        )
        db_session.add(target_user)
        await db_session.commit()

        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                headers = {"Authorization": f"Bearer {d['admin_token']}", "X-Tenant-ID": str(d["tenant_a_id"])}

                # CREATE
                resp = await c.post(
                    "/api/asignaciones",
                    json={
                        "usuario_id": str(target_user.id),
                        "rol_id": str(d["profe_rol_id"]),
                        "desde": "2026-01-01",
                        "hasta": "2026-12-31",
                    },
                    headers=headers,
                )
                assert resp.status_code == 201
                body = resp.json()
                assert body["usuario_id"] == str(target_user.id)
                assert body["rol_id"] == str(d["profe_rol_id"])
                assert body["desde"] == "2026-01-01"
                assert body["hasta"] == "2026-12-31"
                asig_id = body["id"]

                # LIST
                resp = await c.get(
                    "/api/asignaciones",
                    headers=headers,
                )
                assert resp.status_code == 200
                ids = [a["id"] for a in resp.json()]
                assert asig_id in ids

                # GET
                resp = await c.get(
                    f"/api/asignaciones/{asig_id}",
                    headers=headers,
                )
                assert resp.status_code == 200
                assert resp.json()["id"] == asig_id

                # UPDATE
                resp = await c.put(
                    f"/api/asignaciones/{asig_id}",
                    json={"hasta": "2026-06-30"},
                    headers=headers,
                )
                assert resp.status_code == 200
                assert resp.json()["hasta"] == "2026-06-30"

                # SOFT DELETE
                resp = await c.delete(
                    f"/api/asignaciones/{asig_id}",
                    headers=headers,
                )
                assert resp.status_code == 204

                resp = await c.get(
                    f"/api/asignaciones/{asig_id}",
                    headers=headers,
                )
                assert resp.status_code == 404


@pytest.mark.needs_db
class TestVigencia:
    """9.6: Asignación vencida no da permisos; vigente sí."""

    async def test_asignacion_vencida_no_autoriza(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        target_user = User(
            email="vencida@test.com", password_hash="hash",
            nombre="Vencida", apellidos="Test", tenant_id=d["tenant_a_id"],
        )
        db_session.add(target_user)
        await db_session.commit()

        svc = AsignacionService(db_session, d["tenant_a_id"])

        from app.schemas.asignacion import AsignacionCreate
        asig = await svc.create(AsignacionCreate(
            usuario_id=target_user.id,
            rol_id=d["profe_rol_id"],
            desde=date(2020, 1, 1),
            hasta=date(2020, 12, 31),
        ))
        assert not svc.is_vigente(Asignacion(
            desde=asig.desde, hasta=asig.hasta,
        ))

        from app.core.permissions import PermissionService
        perms = await PermissionService(db_session).get_effective_permissions(
            target_user.id, d["tenant_a_id"],
        )
        assert "calificaciones:importar" not in perms

    async def test_asignacion_vigente_autoriza(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        target_user = User(
            email="vigente@test.com", password_hash="hash",
            nombre="Vigente", apellidos="Test", tenant_id=d["tenant_a_id"],
        )
        db_session.add(target_user)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc = AsignacionService(db_session, d["tenant_a_id"])
        await svc.create(AsignacionCreate(
            usuario_id=target_user.id,
            rol_id=d["profe_rol_id"],
            desde=date(2025, 1, 1),
        ))

        from app.core.permissions import PermissionService
        perms = await PermissionService(db_session).get_effective_permissions(
            target_user.id, d["tenant_a_id"],
        )
        assert "calificaciones:importar" in perms


@pytest.mark.needs_db
class TestMultiRol:
    """9.7: Usuario con 2 asignaciones vigentes tiene unión de permisos."""

    async def test_multi_rol_union_permisos(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        target_user = User(
            email="multirole@test.com", password_hash="hash",
            nombre="Multi", apellidos="Role", tenant_id=d["tenant_a_id"],
        )
        db_session.add(target_user)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc = AsignacionService(db_session, d["tenant_a_id"])

        # PROFESOR → calificaciones:importar
        await svc.create(AsignacionCreate(
            usuario_id=target_user.id, rol_id=d["profe_rol_id"],
            desde=date(2025, 1, 1),
        ))
        # COORDINADOR → comunicacion:enviar
        await svc.create(AsignacionCreate(
            usuario_id=target_user.id, rol_id=d["coord_rol_id"],
            desde=date(2025, 1, 1),
        ))

        from app.core.permissions import PermissionService
        perms = await PermissionService(db_session).get_effective_permissions(
            target_user.id, d["tenant_a_id"],
        )
        assert "calificaciones:importar" in perms
        assert "comunicacion:enviar" in perms


@pytest.mark.needs_db
class TestJerarquia:
    """9.8: Asignación con responsable_id."""

    async def test_asignacion_con_responsable(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        responsable = User(
            email="responsable@test.com", password_hash="hash",
            nombre="Responsable", apellidos="Test", tenant_id=d["tenant_a_id"],
        )
        db_session.add(responsable)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc = AsignacionService(db_session, d["tenant_a_id"])
        asig = await svc.create(AsignacionCreate(
            usuario_id=responsable.id,
            rol_id=d["profe_rol_id"],
            responsable_id=d["admin_user_id"],
            desde=date(2026, 1, 1),
        ))
        assert asig.responsable_id == d["admin_user_id"]


@pytest.mark.needs_db
class TestFiltrosAsignacion:
    """9.9: Filtros por materia, vigencia, usuario, rol."""

    async def test_filtros(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        user_a = User(email="filtro_a@test.com", password_hash="hash",
                      nombre="FiltroA", apellidos="Test", tenant_id=d["tenant_a_id"])
        user_b = User(email="filtro_b@test.com", password_hash="hash",
                      nombre="FiltroB", apellidos="Test", tenant_id=d["tenant_a_id"])
        db_session.add(user_a)
        db_session.add(user_b)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc = AsignacionService(db_session, d["tenant_a_id"])

        await svc.create(AsignacionCreate(
            usuario_id=user_a.id, rol_id=d["profe_rol_id"],
            materia_id=d["materia_id"], desde=date(2026, 1, 1),
        ))
        await svc.create(AsignacionCreate(
            usuario_id=user_b.id, rol_id=d["coord_rol_id"],
            desde=date(2026, 1, 1),
        ))

        # Filter by materia
        result = await svc.list(materia_id=d["materia_id"])
        assert len(result) == 1
        assert result[0].usuario_id == user_a.id

        # Filter by usuario
        result = await svc.list(usuario_id=user_b.id)
        assert len(result) == 1

        # Filter by rol
        result = await svc.list(rol_id=d["coord_rol_id"])
        assert len(result) == 1
        assert result[0].rol_id == d["coord_rol_id"]

        # Filter by vigente
        result = await svc.list(vigente=True)
        assert len(result) >= 2


@pytest.mark.needs_db
class TestMultiTenantAsignacion:
    """9.10: Aislamiento multi-tenant — Tenant A no ve datos de Tenant B."""

    async def test_tenant_b_no_ve_asignaciones_de_a(self, setup_equipos_data, db_session, tenant_b):
        d = setup_equipos_data
        settings = Settings()

        # Create user in tenant A
        user_a = User(
            email="user_a_aislado@test.com", password_hash="hash",
            nombre="UserA", apellidos="Isolated", tenant_id=d["tenant_a_id"],
        )
        db_session.add(user_a)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc_a = AsignacionService(db_session, d["tenant_a_id"])
        await svc_a.create(AsignacionCreate(
            usuario_id=user_a.id, rol_id=d["profe_rol_id"],
            desde=date(2026, 1, 1),
        ))

        # Create admin in tenant B
        admin_rol_b = Rol(nombre="ADMIN_B_ASIG", descripcion="Admin B", tenant_id=tenant_b.id)
        db_session.add(admin_rol_b)
        await db_session.flush()

        perm = await db_session.execute(
            select(Permiso).where(Permiso.codigo == "equipos:asignar")
        )
        perm = perm.scalar_one()
        db_session.add(RolPermiso(rol_id=admin_rol_b.id, permiso_id=perm.id, tenant_id=tenant_b.id))

        admin_b = User(
            email="admin_b_asig@test.com", password_hash=hash_password("pass123!"),
            nombre="Admin", apellidos="BAsig", tenant_id=tenant_b.id,
        )
        db_session.add(admin_b)
        await db_session.flush()
        db_session.add(UsuarioRol(
            user_id=admin_b.id, rol_id=admin_rol_b.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
            tenant_id=tenant_b.id,
        ))
        await db_session.commit()

        token_b = jwt.encode(
            {"sub": str(admin_b.id), "tenant_id": str(tenant_b.id),
             "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )

        client, app = _make_client()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                resp = await c.get(
                    "/api/asignaciones",
                    headers={"Authorization": f"Bearer {token_b}", "X-Tenant-ID": str(tenant_b.id)},
                )
                assert resp.status_code == 200
                assert len(resp.json()) == 0


@pytest.mark.needs_db
class TestSoftDeleteAsignacion:
    """9.11: Soft delete en asignacion."""

    async def test_soft_delete_marca_deleted_at(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        user = User(
            email="softdel@test.com", password_hash="hash",
            nombre="Soft", apellidos="Delete", tenant_id=d["tenant_a_id"],
        )
        db_session.add(user)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc = AsignacionService(db_session, d["tenant_a_id"])
        asig = await svc.create(AsignacionCreate(
            usuario_id=user.id, rol_id=d["profe_rol_id"],
            desde=date(2026, 1, 1),
        ))

        await svc.soft_delete(asig.id)

        # GET returns 404
        with pytest.raises(Exception) as exc:
            await svc.get(asig.id)
        assert "404" in str(exc) or "no encontrada" in str(exc).lower()

        # Raw DB check
        stmt = select(Asignacion).where(Asignacion.id == asig.id)
        result = await db_session.execute(stmt)
        entity = result.scalar_one()
        assert entity.deleted_at is not None


@pytest.mark.needs_db
class TestPermissionServiceAsignacion:
    """Additional test: PermissionService now considers Asignacion."""

    async def test_asignacion_vigente_otorga_permisos(self, setup_equipos_data, db_session):
        d = setup_equipos_data
        user = User(
            email="perm_asig@test.com", password_hash="hash",
            nombre="Perm", apellidos="Asig", tenant_id=d["tenant_a_id"],
        )
        db_session.add(user)
        await db_session.commit()

        from app.schemas.asignacion import AsignacionCreate
        svc = AsignacionService(db_session, d["tenant_a_id"])
        await svc.create(AsignacionCreate(
            usuario_id=user.id, rol_id=d["profe_rol_id"],
            desde=date(2025, 1, 1),
        ))

        from app.core.permissions import PermissionService
        perms = await PermissionService(db_session).get_effective_permissions(
            user.id, d["tenant_a_id"],
        )
        assert "calificaciones:importar" in perms


@pytest.mark.needs_db
class TestMigration008:
    """9.13: Migration 008 — verify metadata and idempotent SQL."""

    async def test_migration_metadata(self):
        """Verify migration has correct revision and references."""
        from alembic.script import ScriptDirectory
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        # Get migration 008 by revision
        rev = script.get_revision("008")
        assert rev is not None
        assert rev.down_revision == "007"
        assert "usuarios" in rev.doc or "asignaciones" in rev.doc

    async def test_migration_revision_chain(self):
        """Verify migration 008 is properly linked in the revision chain."""
        from alembic.script import ScriptDirectory
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        script = ScriptDirectory.from_config(alembic_cfg)

        rev = script.get_revision("008")
        assert rev is not None
        assert rev.down_revision == "007"
        # Walk all migrations from head to base to ensure chain is intact
        revisions = list(script.walk_revisions())
        revisions.sort(key=lambda r: r.revision)
        assert len(revisions) >= 8
        assert revisions[0].revision == "001"
