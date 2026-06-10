"""Tests RED para PermissionService (Grupo 2)."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.permissions import PermissionService
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
async def seed_rbac(db_session, tenant_a, tenant_b):
    """Crea roles, permisos y asignaciones base para tests."""
    roles_data = {
        "PROFESOR": Rol(nombre="PROFESOR", descripcion="Teacher", tenant_id=tenant_a.id),
        "COORDINADOR": Rol(nombre="COORDINADOR", descripcion="Coordinator", tenant_id=tenant_a.id),
        "ALUMNO": Rol(nombre="ALUMNO", descripcion="Student", tenant_id=tenant_a.id),
        "ADMIN_B": Rol(nombre="ADMIN", descripcion="Admin B", tenant_id=tenant_b.id),
    }
    for r in roles_data.values():
        db_session.add(r)
    await db_session.flush()

    perms_data = {
        "calificaciones:importar": Permiso(
            codigo="calificaciones:importar",
            descripcion="Importar calificaciones",
            modulo="calificaciones",
        ),
        "atrasados:ver": Permiso(
            codigo="atrasados:ver",
            descripcion="Ver atrasados",
            modulo="atrasados",
        ),
        "comunicacion:enviar": Permiso(
            codigo="comunicacion:enviar",
            descripcion="Enviar comunicaciones",
            modulo="comunicacion",
        ),
        "estado:ver_propio": Permiso(
            codigo="estado:ver_propio",
            descripcion="Ver estado propio",
            modulo="estado",
        ),
    }
    for p in perms_data.values():
        db_session.add(p)
    await db_session.flush()

    # PROFESOR → calificaciones:importar, atrasados:ver
    db_session.add(RolPermiso(
        rol_id=roles_data["PROFESOR"].id,
        permiso_id=perms_data["calificaciones:importar"].id,
        tenant_id=tenant_a.id,
    ))
    db_session.add(RolPermiso(
        rol_id=roles_data["PROFESOR"].id,
        permiso_id=perms_data["atrasados:ver"].id,
        tenant_id=tenant_a.id,
    ))
    # COORDINADOR → comunicacion:enviar, atrasados:ver
    db_session.add(RolPermiso(
        rol_id=roles_data["COORDINADOR"].id,
        permiso_id=perms_data["comunicacion:enviar"].id,
        tenant_id=tenant_a.id,
    ))
    db_session.add(RolPermiso(
        rol_id=roles_data["COORDINADOR"].id,
        permiso_id=perms_data["atrasados:ver"].id,
        tenant_id=tenant_a.id,
    ))
    # ALUMNO → estado:ver_propio
    db_session.add(RolPermiso(
        rol_id=roles_data["ALUMNO"].id,
        permiso_id=perms_data["estado:ver_propio"].id,
        tenant_id=tenant_a.id,
    ))
    await db_session.commit()

    return {
        "roles": roles_data,
        "perms": perms_data,
    }


@pytest.fixture
async def user_profesor(db_session, tenant_a, seed_rbac):
    user = User(
        email="profesor@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Profe", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()
    ur = UsuarioRol(
        user_id=user.id,
        rol_id=seed_rbac["roles"]["PROFESOR"].id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)
    await db_session.commit()
    return user


@pytest.fixture
async def user_profesor_coordinador(db_session, tenant_a, seed_rbac):
    user = User(
        email="profycoord@test.com",
        password_hash=hash_password("pass123!"),
        nombre="ProfeCoord", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()
    for rol_name in ["PROFESOR", "COORDINADOR"]:
        ur = UsuarioRol(
            user_id=user.id,
            rol_id=seed_rbac["roles"][rol_name].id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
            tenant_id=tenant_a.id,
        )
        db_session.add(ur)
    await db_session.commit()
    return user


@pytest.fixture
async def user_rol_vencido(db_session, tenant_a, seed_rbac):
    user = User(
        email="vencido@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Vencido", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()
    ur = UsuarioRol(
        user_id=user.id,
        rol_id=seed_rbac["roles"]["PROFESOR"].id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=60),
        fecha_hasta=datetime.now(timezone.utc) - timedelta(days=1),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)
    await db_session.commit()
    return user


@pytest.fixture
async def user_sin_roles(db_session, tenant_a):
    user = User(
        email="sinroles@test.com",
        password_hash=hash_password("pass123!"),
        nombre="SinRoles", apellidos="",
        tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.needs_db
class TestPermissionService:
    async def test_usuario_con_rol_profesor_obtiene_permisos(
        self, db_session, tenant_a, user_profesor,
    ):
        svc = PermissionService(db_session)
        perms = await svc.get_effective_permissions(user_profesor.id, tenant_a.id)
        assert "calificaciones:importar" in perms
        assert "atrasados:ver" in perms
        assert "comunicacion:enviar" not in perms

    async def test_usuario_con_profesor_y_coordinador_obtiene_union(
        self, db_session, tenant_a, user_profesor_coordinador,
    ):
        svc = PermissionService(db_session)
        perms = await svc.get_effective_permissions(
            user_profesor_coordinador.id, tenant_a.id,
        )
        assert "calificaciones:importar" in perms
        assert "atrasados:ver" in perms
        assert "comunicacion:enviar" in perms
        assert len(perms) == 3

    async def test_permiso_fuera_de_vigencia_no_se_incluye(
        self, db_session, tenant_a, user_rol_vencido,
    ):
        svc = PermissionService(db_session)
        perms = await svc.get_effective_permissions(user_rol_vencido.id, tenant_a.id)
        assert len(perms) == 0

    async def test_usuario_tenant_a_no_ve_permisos_tenant_b(
        self, db_session, tenant_a, tenant_b, user_profesor,
    ):
        svc = PermissionService(db_session)
        perms = await svc.get_effective_permissions(user_profesor.id, tenant_b.id)
        assert len(perms) == 0

    async def test_fail_closed_usuario_sin_roles_devuelve_vacio(
        self, db_session, tenant_a, user_sin_roles,
    ):
        svc = PermissionService(db_session)
        perms = await svc.get_effective_permissions(user_sin_roles.id, tenant_a.id)
        assert len(perms) == 0

    async def test_usuario_sin_ningun_permiso_devuelve_vacio(
        self, db_session, tenant_a, seed_rbac,
    ):
        user = User(
            email="noperms@test.com",
            password_hash=hash_password("pass123!"),
            nombre="NoPerms", apellidos="",
            tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()
        ur = UsuarioRol(
            user_id=user.id,
            rol_id=seed_rbac["roles"]["ALUMNO"].id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
            tenant_id=tenant_a.id,
        )
        db_session.add(ur)
        await db_session.commit()

        svc = PermissionService(db_session)
        perms = await svc.get_effective_permissions(user.id, tenant_a.id)
        assert "estado:ver_propio" in perms
