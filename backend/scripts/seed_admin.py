"""Seed script: crea el primer tenant, permisos, rol ADMIN y usuario admin.

Uso: python -m scripts.seed_admin
Correr UNA SOLA VEZ (es idempotente: saltea si ya existe un admin).
"""

import asyncio
import uuid
from datetime import datetime, timezone

from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.rol import Rol
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.models.user import User
from app.models.usuario_rol import UsuarioRol
from sqlalchemy import select


# ── Config ──────────────────────────────────────────────────────────
TENANT_NOMBRE = "Institución Demo"
TENANT_SLUG = "demo"
ADMIN_EMAIL = "admin@trace.com"
ADMIN_PASSWORD = "admin1234"  # cambiá en producción
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDOS = "Sistema"

PERMISOS = [
    ("usuarios:gestionar", "Gestionar usuarios y roles", "usuarios"),
    ("estructura:gestionar", "Gestionar estructura académica", "estructura"),
    ("padron:importar", "Importar y gestionar padrón", "padron"),
    ("calificaciones:importar", "Importar y gestionar calificaciones", "calificaciones"),
    ("comunicacion:enviar", "Enviar comunicaciones", "comunicacion"),
    ("comunicacion:aprobar", "Aprobar comunicaciones", "comunicacion"),
    ("avisos:publicar", "Publicar avisos", "avisos"),
    ("equipos:ver_propio", "Ver equipo propio", "equipos"),
    ("equipos:asignar", "Asignar equipos docentes", "equipos"),
    ("auditoria:ver", "Ver auditoría", "auditoria"),
    ("impersonacion:usar", "Usar impersonación", "auth"),
    ("atrasados:ver", "Ver análisis de atrasados", "analisis"),
]


async def seed():
    settings = Settings(
        _env_file=r"C:\Users\AyP computacion\Desktop\Facultad\FACULTAD\cuarto semestre\2026\Gestion de desarrollo de software\active-trace\backend\.env",
    )
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        # Chequear si ya existe un admin
        result = await session.execute(
            select(User).join(UsuarioRol).join(Rol).where(Rol.nombre == "ADMIN")
        )
        existing = result.scalars().first()
        if existing:
            print(f"ℹ️  Admin ya existe: {existing.email}")
            print("No se hizo nada (seed idempotente).")
            await engine.dispose()
            return

        # 1. Tenant
        tenant = Tenant(nombre=TENANT_NOMBRE, slug=TENANT_SLUG)
        session.add(tenant)
        await session.flush()
        print(f"OK Tenant creado: {tenant.nombre} (id={tenant.id})")

        # 2. Crear permisos únicos
        permiso_map: dict[str, Permiso] = {}
        for codigo, descripcion, modulo in PERMISOS:
            result = await session.execute(
                select(Permiso).where(Permiso.codigo == codigo)
            )
            existing_perm = result.scalars().first()
            if existing_perm:
                permiso_map[codigo] = existing_perm
            else:
                permiso = Permiso(codigo=codigo, descripcion=descripcion, modulo=modulo)
                session.add(permiso)
                await session.flush()
                permiso_map[codigo] = permiso
        print(f"OK {len(permiso_map)} permisos asegurados")

        # 3. Rol ADMIN
        rol = Rol(nombre="ADMIN", descripcion="Administrador del sistema")
        session.add(rol)
        await session.flush()
        print(f"OK Rol ADMIN creado (id={rol.id})")

        # 4. Asignar todos los permisos al rol ADMIN
        for permiso in permiso_map.values():
            rp = RolPermiso(rol_id=rol.id, permiso_id=permiso.id, tenant_id=tenant.id)
            session.add(rp)
        print(f"OK {len(permiso_map)} permisos asignados al rol ADMIN")

        # 5. Crear usuario admin
        user = User(
            tenant_id=tenant.id,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            nombre=ADMIN_NOMBRE,
            apellidos=ADMIN_APELLIDOS,
            activo=True,
        )
        session.add(user)
        await session.flush()
        print(f"OK Usuario admin creado: {user.email}")

        # 6. Asignar rol ADMIN al usuario
        ur = UsuarioRol(
            user_id=user.id,
            rol_id=rol.id,
            fecha_desde=datetime.now(timezone.utc),
            tenant_id=tenant.id,
        )
        session.add(ur)
        await session.flush()

        await session.commit()
        print(f"\nSeed completado!")
        print(f"   Tenant:   {TENANT_SLUG}")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
