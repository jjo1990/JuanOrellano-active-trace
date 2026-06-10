"""Tests RED para modelos RBAC (Grupo 1)."""

import uuid

import pytest
from sqlalchemy import select

from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol
from app.models.user import User
from app.core.security import hash_password


@pytest.mark.needs_db
class TestRolModel:
    async def test_crear_rol_con_nombre_unique_por_tenant(
        self, db_session, tenant_a, tenant_b,
    ):
        r1 = Rol(nombre="ADMIN", descripcion="Admin")
        r1.tenant_id = tenant_a.id
        db_session.add(r1)
        await db_session.commit()

        r2 = Rol(nombre="ADMIN", descripcion="Admin B")
        r2.tenant_id = tenant_b.id
        db_session.add(r2)
        await db_session.commit()

        stmt = select(Rol).where(Rol.nombre == "ADMIN")
        result = await db_session.execute(stmt)
        roles = result.scalars().all()
        assert len(roles) == 2

    async def test_rol_repite_nombre_mismo_tenant_falla(self, db_session, tenant_a):
        r1 = Rol(nombre="PROFESOR", descripcion="Teacher")
        r1.tenant_id = tenant_a.id
        db_session.add(r1)
        await db_session.commit()

        r2 = Rol(nombre="PROFESOR", descripcion="Duplicate")
        r2.tenant_id = tenant_a.id
        db_session.add(r2)
        with pytest.raises(Exception):
            await db_session.commit()
        await db_session.rollback()

    async def test_rol_hereda_base_model_mixin(self, db_session, tenant_a):
        r = Rol(nombre="TEST", descripcion="Test")
        r.tenant_id = tenant_a.id
        db_session.add(r)
        await db_session.commit()

        assert r.id is not None
        assert r.tenant_id == tenant_a.id
        assert r.created_at is not None
        assert r.deleted_at is None


@pytest.mark.needs_db
class TestPermisoModel:
    async def test_crear_permiso_con_codigo_unique_global(self, db_session):
        p1 = Permiso(
            codigo="calificaciones:importar",
            descripcion="Importar calificaciones",
            modulo="calificaciones",
        )
        db_session.add(p1)
        await db_session.commit()

        p2 = Permiso(
            codigo="atrasados:ver",
            descripcion="Ver atrasados",
            modulo="atrasados",
        )
        db_session.add(p2)
        await db_session.commit()

        assert p1.id != p2.id

    async def test_permiso_repite_codigo_falla(self, db_session):
        p1 = Permiso(
            codigo="calificaciones:importar",
            descripcion="Original",
            modulo="calificaciones",
        )
        db_session.add(p1)
        await db_session.commit()

        p2 = Permiso(
            codigo="calificaciones:importar",
            descripcion="Duplicate",
            modulo="calificaciones",
        )
        db_session.add(p2)
        with pytest.raises(Exception):
            await db_session.commit()
        await db_session.rollback()

    async def test_permiso_hereda_base_model_mixin(self, db_session):
        p = Permiso(
            codigo="test:permiso",
            descripcion="Test",
            modulo="test",
        )
        db_session.add(p)
        await db_session.commit()

        assert p.id is not None
        assert p.codigo == "test:permiso"
        assert p.created_at is not None
        assert p.deleted_at is None

    async def test_permiso_no_tiene_tenant_id(self, db_session):
        p = Permiso(
            codigo="test:notenant",
            descripcion="Global",
            modulo="test",
        )
        db_session.add(p)
        await db_session.commit()
        assert p.tenant_id is None


@pytest.mark.needs_db
class TestRolPermisoModel:
    async def test_crear_rol_permiso_con_fk(self, db_session, tenant_a):
        rol = Rol(nombre="ADMIN", descripcion="Admin")
        rol.tenant_id = tenant_a.id
        db_session.add(rol)
        await db_session.flush()

        perm = Permiso(codigo="test:accion", descripcion="Test", modulo="test")
        db_session.add(perm)
        await db_session.flush()

        rp = RolPermiso(rol_id=rol.id, permiso_id=perm.id)
        rp.tenant_id = tenant_a.id
        db_session.add(rp)
        await db_session.commit()

        assert rp.id is not None
        assert rp.rol_id == rol.id
        assert rp.permiso_id == perm.id

    async def test_rol_permiso_unique_compuesto(self, db_session, tenant_a):
        rol = Rol(nombre="EDITOR", descripcion="Editor")
        rol.tenant_id = tenant_a.id
        db_session.add(rol)
        await db_session.flush()

        perm = Permiso(codigo="editor:write", descripcion="Write", modulo="editor")
        db_session.add(perm)
        await db_session.flush()

        rp1 = RolPermiso(rol_id=rol.id, permiso_id=perm.id)
        rp1.tenant_id = tenant_a.id
        db_session.add(rp1)
        await db_session.commit()

        rp2 = RolPermiso(rol_id=rol.id, permiso_id=perm.id)
        rp2.tenant_id = tenant_a.id
        db_session.add(rp2)
        with pytest.raises(Exception):
            await db_session.commit()
        await db_session.rollback()

    async def test_rol_permiso_mismo_par_distinto_tenant_ok(
        self, db_session, tenant_a, tenant_b,
    ):
        rol_a = Rol(nombre="VIEWER", descripcion="Viewer A")
        rol_a.tenant_id = tenant_a.id
        db_session.add(rol_a)
        rol_b = Rol(nombre="VIEWER", descripcion="Viewer B")
        rol_b.tenant_id = tenant_b.id
        db_session.add(rol_b)
        await db_session.flush()

        perm = Permiso(codigo="viewer:read", descripcion="Read", modulo="viewer")
        db_session.add(perm)
        await db_session.flush()

        rp_a = RolPermiso(rol_id=rol_a.id, permiso_id=perm.id)
        rp_a.tenant_id = tenant_a.id
        db_session.add(rp_a)
        rp_b = RolPermiso(rol_id=rol_b.id, permiso_id=perm.id)
        rp_b.tenant_id = tenant_b.id
        db_session.add(rp_b)
        await db_session.commit()

        stmt = select(RolPermiso).where(RolPermiso.permiso_id == perm.id)
        result = await db_session.execute(stmt)
        assert len(result.scalars().all()) == 2


@pytest.mark.needs_db
class TestUsuarioRolModel:
    async def test_crear_usuario_rol_con_fks(self, db_session, tenant_a):
        user = User(
            email="test@test.com",
            password_hash=hash_password("pass123!"),
            nombre="Test", apellidos="",
        )
        user.tenant_id = tenant_a.id
        db_session.add(user)
        await db_session.flush()

        rol = Rol(nombre="ALUMNO", descripcion="Student")
        rol.tenant_id = tenant_a.id
        db_session.add(rol)
        await db_session.flush()

        from datetime import datetime, timezone

        ur = UsuarioRol(
            user_id=user.id,
            rol_id=rol.id,
            fecha_desde=datetime.now(timezone.utc),
        )
        ur.tenant_id = tenant_a.id
        db_session.add(ur)
        await db_session.commit()

        assert ur.id is not None
        assert ur.user_id == user.id
        assert ur.rol_id == rol.id
        assert ur.fecha_desde is not None
        assert ur.fecha_hasta is None

    async def test_usuario_rol_fecha_hasta_nullable(self, db_session, tenant_a):
        user = User(
            email="vigencia@test.com",
            password_hash=hash_password("pass123!"),
            nombre="Vigencia", apellidos="",
        )
        user.tenant_id = tenant_a.id
        db_session.add(user)
        await db_session.flush()

        rol = Rol(nombre="TUTOR", descripcion="Tutor")
        rol.tenant_id = tenant_a.id
        db_session.add(rol)
        await db_session.flush()

        from datetime import datetime, timedelta, timezone

        ahora = datetime.now(timezone.utc)
        ur = UsuarioRol(
            user_id=user.id,
            rol_id=rol.id,
            fecha_desde=ahora - timedelta(days=30),
            fecha_hasta=ahora + timedelta(days=30),
        )
        ur.tenant_id = tenant_a.id
        db_session.add(ur)
        await db_session.commit()

        assert ur.fecha_hasta is not None

    async def test_usuario_rol_hereda_base_model_mixin(self, db_session, tenant_a):
        user = User(
            email="mixin@test.com",
            password_hash=hash_password("pass123!"),
            nombre="Mixin", apellidos="",
        )
        user.tenant_id = tenant_a.id
        db_session.add(user)
        await db_session.flush()

        rol = Rol(nombre="ADMIN", descripcion="Admin")
        rol.tenant_id = tenant_a.id
        db_session.add(rol)
        await db_session.flush()

        from datetime import datetime, timezone

        ur = UsuarioRol(
            user_id=user.id,
            rol_id=rol.id,
            fecha_desde=datetime.now(timezone.utc),
        )
        ur.tenant_id = tenant_a.id
        db_session.add(ur)
        await db_session.commit()

        assert ur.created_at is not None
        assert ur.deleted_at is None
