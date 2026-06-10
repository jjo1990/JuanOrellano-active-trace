"""RBAC: create rol, permiso, rol_permiso, usuario_rol tables + seed + migrate

Revision ID: 005
Revises: 004
Create Date: 2026-06-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── helpers ──────────────────────────────────────────────────────────────


def _create_tables() -> None:
    op.create_table(
        "rol",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.String(255), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_rol_nombre_tenant", "rol", ["nombre", "tenant_id"])

    op.create_table(
        "permiso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.String(255), nullable=False),
        sa.Column("modulo", sa.String(100), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        # Permiso no tiene tenant_id (global)
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_unique_constraint("uq_permiso_codigo", "permiso", ["codigo"])

    op.create_table(
        "rol_permiso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("rol_id", UUID(as_uuid=True), sa.ForeignKey("rol.id"), nullable=False),
        sa.Column("permiso_id", UUID(as_uuid=True), sa.ForeignKey("permiso.id"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_rol_permiso", "rol_permiso", ["rol_id", "permiso_id", "tenant_id"])

    op.create_table(
        "usuario_rol",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("rol_id", UUID(as_uuid=True), sa.ForeignKey("rol.id"), nullable=False),
        sa.Column("fecha_desde", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("fecha_hasta", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_usuario_rol", "usuario_rol", ["user_id", "rol_id", "fecha_desde"])


# ── seed data ────────────────────────────────────────────────────────────

ROLES = [
    ("ALUMNO", "Estudiante que cursa materias"),
    ("TUTOR", "Auxiliar / ayudante de cátedra"),
    ("PROFESOR", "Docente a cargo de una o más comisiones"),
    ("COORDINADOR", "Responsable de un conjunto de materias o cohorte"),
    ("NEXO", "Rol de articulación / enlace transversal"),
    ("ADMIN", "Administrador del sistema dentro del tenant"),
    ("FINANZAS", "Responsable de liquidaciones y honorarios"),
]

PERMISOS = [
    ("estado:ver_propio", "Ver estado académico propio", "estado"),
    ("evaluaciones:reservar", "Reservar instancia de evaluación", "evaluaciones"),
    ("avisos:confirmar", "Confirmar avisos (acknowledgment)", "avisos"),
    ("calificaciones:importar", "Importar calificaciones", "calificaciones"),
    ("atrasados:ver", "Ver alumnos atrasados", "atrasados"),
    ("entregas:detectar_sin_corregir", "Detectar entregas sin corregir", "entregas"),
    ("comunicacion:enviar", "Enviar comunicaciones a alumnos", "comunicacion"),
    ("comunicacion:aprobar", "Aprobar comunicaciones masivas", "comunicacion"),
    ("encuentros:gestionar", "Gestionar encuentros", "encuentros"),
    ("guardias:registrar", "Registrar guardias", "guardias"),
    ("tareas:gestionar", "Gestionar tareas internas", "tareas"),
    ("avisos:publicar", "Publicar avisos", "avisos"),
    ("equipos:asignar", "Gestionar equipos docentes (asignaciones)", "equipos"),
    ("estructura:gestionar", "Gestionar estructura académica (carreras, cohortes, materias)", "estructura"),
    ("usuarios:gestionar", "Gestionar usuarios del tenant", "usuarios"),
    ("auditoria:ver", "Ver auditoría", "auditoria"),
    ("liquidaciones:grilla", "Operar grilla salarial", "liquidaciones"),
    ("liquidaciones:calcular", "Calcular / cerrar liquidaciones", "liquidaciones"),
    ("facturas:gestionar", "Gestionar facturas", "facturas"),
    ("tenant:configurar", "Configurar el tenant", "tenant"),
]

# Matrix from 03_actores_y_roles.md §3.3
# (rol_name, permiso_codigo) tuples
MATRIZ = [
    # ALUMNO
    ("ALUMNO", "estado:ver_propio"),
    ("ALUMNO", "evaluaciones:reservar"),
    ("ALUMNO", "avisos:confirmar"),
    # TUTOR
    ("TUTOR", "avisos:confirmar"),
    ("TUTOR", "atrasados:ver"),
    ("TUTOR", "entregas:detectar_sin_corregir"),
    ("TUTOR", "encuentros:gestionar"),
    ("TUTOR", "guardias:registrar"),
    # PROFESOR
    ("PROFESOR", "avisos:confirmar"),
    ("PROFESOR", "calificaciones:importar"),
    ("PROFESOR", "atrasados:ver"),
    ("PROFESOR", "entregas:detectar_sin_corregir"),
    ("PROFESOR", "comunicacion:enviar"),
    ("PROFESOR", "encuentros:gestionar"),
    ("PROFESOR", "guardias:registrar"),
    ("PROFESOR", "tareas:gestionar"),
    # COORDINADOR
    ("COORDINADOR", "avisos:confirmar"),
    ("COORDINADOR", "calificaciones:importar"),
    ("COORDINADOR", "atrasados:ver"),
    ("COORDINADOR", "entregas:detectar_sin_corregir"),
    ("COORDINADOR", "comunicacion:enviar"),
    ("COORDINADOR", "comunicacion:aprobar"),
    ("COORDINADOR", "encuentros:gestionar"),
    ("COORDINADOR", "guardias:registrar"),
    ("COORDINADOR", "tareas:gestionar"),
    ("COORDINADOR", "avisos:publicar"),
    ("COORDINADOR", "equipos:asignar"),
    ("COORDINADOR", "auditoria:ver"),
    # ADMIN
    ("ADMIN", "avisos:confirmar"),
    ("ADMIN", "calificaciones:importar"),
    ("ADMIN", "atrasados:ver"),
    ("ADMIN", "entregas:detectar_sin_corregir"),
    ("ADMIN", "comunicacion:enviar"),
    ("ADMIN", "comunicacion:aprobar"),
    ("ADMIN", "encuentros:gestionar"),
    ("ADMIN", "guardias:registrar"),
    ("ADMIN", "tareas:gestionar"),
    ("ADMIN", "avisos:publicar"),
    ("ADMIN", "equipos:asignar"),
    ("ADMIN", "estructura:gestionar"),
    ("ADMIN", "usuarios:gestionar"),
    ("ADMIN", "auditoria:ver"),
    ("ADMIN", "tenant:configurar"),
    # FINANZAS
    ("FINANZAS", "avisos:confirmar"),
    ("FINANZAS", "auditoria:ver"),
    ("FINANZAS", "liquidaciones:grilla"),
    ("FINANZAS", "liquidaciones:calcular"),
    ("FINANZAS", "facturas:gestionar"),
    # NEXO — sin permisos (PA-25)
]


def _seed_roles() -> dict[str, str]:
    """Inserta roles y devuelve {nombre: id} (como string)."""
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("rol",))
    tbl = sa.Table("rol", meta)
    ids = {}
    for name, desc in ROLES:
        # Insertar con un ID fijo (UUID v4) para referencia en seed posterior
        import uuid
        rid = str(uuid.uuid4())
        conn.execute(
            tbl.insert().values(id=rid, nombre=name, descripcion=desc, tenant_id=None)
        )
        ids[name] = rid
    return ids


def _seed_permisos() -> dict[str, str]:
    """Inserta permisos y devuelve {codigo: id}."""
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso",))
    tbl = sa.Table("permiso", meta)
    ids = {}
    for codigo, desc, modulo in PERMISOS:
        import uuid
        pid = str(uuid.uuid4())
        conn.execute(
            tbl.insert().values(id=pid, codigo=codigo, descripcion=desc, modulo=modulo, tenant_id=None)
        )
        ids[codigo] = pid
    return ids


def _seed_matriz(rol_ids: dict[str, str], permiso_ids: dict[str, str]) -> None:
    """Inserta filas en rol_permiso según la matriz."""
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("rol_permiso",))
    tbl = sa.Table("rol_permiso", meta)
    import uuid
    for rol_name, permiso_codigo in MATRIZ:
        conn.execute(
            tbl.insert().values(
                id=str(uuid.uuid4()),
                rol_id=rol_ids[rol_name],
                permiso_id=permiso_ids[permiso_codigo],
                tenant_id=None,
            )
        )


def _migrate_user_roles() -> None:
    """Migra user.roles JSONB → usuario_rol.

    Lee user.roles de cada usuario, busca el rol por nombre en la tabla rol,
    y crea una fila en usuario_rol con fecha_desde = user.created_at.
    """
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("user", "rol", "usuario_rol"))
    user_tbl = sa.Table("user", meta)
    rol_tbl = sa.Table("rol", meta)
    ur_tbl = sa.Table("usuario_rol", meta)

    import uuid
    from datetime import timezone

    users = conn.execute(user_tbl.select().where(user_tbl.c.deleted_at.is_(None)))
    roles = conn.execute(rol_tbl.select().where(rol_tbl.c.deleted_at.is_(None)))
    rol_map: dict[str, dict] = {}
    for r in roles:
        nombre = r._mapping.get("nombre") or r.nombre
        rol_map[nombre] = dict(r._mapping)

    for u in users:
        u_data = dict(u._mapping)
        raw_roles = u_data.get("roles") or []
        if not raw_roles:
            continue
        created_at = u_data.get("created_at")
        tenant_id = u_data.get("tenant_id")
        user_id = u_data.get("id")
        for rol_name in raw_roles:
            if rol_name in rol_map:
                conn.execute(
                    ur_tbl.insert().values(
                        id=str(uuid.uuid4()),
                        user_id=str(user_id),
                        rol_id=str(rol_map[rol_name]["id"]),
                        tenant_id=str(tenant_id) if tenant_id else None,
                        fecha_desde=created_at if created_at else sa.func.now(),
                        fecha_hasta=None,
                    )
                )


def _drop_user_roles_column() -> None:
    op.drop_column("user", "roles")


def _recreate_user_roles_column() -> None:
    op.add_column(
        "user",
        sa.Column("roles", sa.dialects.postgresql.JSONB,
                  nullable=False, server_default=sa.text("'[]'::jsonb"), default=list),
    )


def _reverse_migrate_user_roles() -> None:
    """Reverse: leer usuario_rol y reconstruir user.roles JSONB."""
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("user", "rol", "usuario_rol"))
    user_tbl = sa.Table("user", meta)
    rol_tbl = sa.Table("rol", meta)
    ur_tbl = sa.Table("usuario_rol", meta)

    roles = conn.execute(rol_tbl.select())
    rol_id_to_name: dict[str, str] = {}
    for r in roles:
        d = dict(r._mapping)
        rol_id_to_name[str(d["id"])] = d["nombre"]

    users = conn.execute(user_tbl.select())
    for u in users:
        u_data = dict(u._mapping)
        uid = str(u_data["id"])
        tenant_id = u_data.get("tenant_id")
        urs = conn.execute(
            ur_tbl.select().where(
                ur_tbl.c.user_id == uid,
                ur_tbl.c.deleted_at.is_(None),
            )
        )
        role_names = []
        for ur in urs:
            ur_data = dict(ur._mapping)
            rname = rol_id_to_name.get(str(ur_data["rol_id"]), "")
            if rname:
                role_names.append(rname)
        conn.execute(
            user_tbl.update().where(user_tbl.c.id == uid).values(roles=role_names)
        )


# ── migration ────────────────────────────────────────────────────────────


def upgrade() -> None:
    _create_tables()
    rol_ids = _seed_roles()
    permiso_ids = _seed_permisos()
    _seed_matriz(rol_ids, permiso_ids)
    _migrate_user_roles()
    _drop_user_roles_column()


def downgrade() -> None:
    _recreate_user_roles_column()
    _reverse_migrate_user_roles()
    op.drop_table("usuario_rol")
    op.drop_table("rol_permiso")
    op.drop_table("permiso")
    op.drop_table("rol")
