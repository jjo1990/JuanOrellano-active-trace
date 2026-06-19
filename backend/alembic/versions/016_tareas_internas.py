"""C-16: create tarea, comentario_tarea + seed tareas:gestionar permiso

Revision ID: 016
Revises: 015
Create Date: 2026-06-16
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISOS = [
    {
        "codigo": "tareas:gestionar",
        "descripcion": "Gestionar tareas internas del tenant",
        "modulo": "tareas",
        "roles": ["COORDINADOR", "ADMIN"],
    },
]


def upgrade() -> None:
    _create_tarea()
    _create_comentario_tarea()
    _seed_permisos()


def downgrade() -> None:
    _remove_permisos()
    op.drop_table("comentario_tarea")
    op.drop_table("tarea")


def _create_tarea() -> None:
    op.create_table(
        "tarea",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=True),
        sa.Column("asignado_a", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("asignado_por", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("estado", sa.String(20), server_default=sa.text("'Pendiente'"), nullable=False),
        sa.Column("descripcion", sa.Text, nullable=False),
        sa.Column("contexto_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_tarea_tenant_asignado_estado", "tarea", ["tenant_id", "asignado_a", "estado"])
    op.create_index("ix_tarea_tenant_materia", "tarea", ["tenant_id", "materia_id"])
    op.create_index("ix_tarea_tenant_estado", "tarea", ["tenant_id", "estado"])


def _create_comentario_tarea() -> None:
    op.create_table(
        "comentario_tarea",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("tarea_id", UUID(as_uuid=True), sa.ForeignKey("tarea.id"), nullable=False),
        sa.Column("autor_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("texto", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_comentario_tarea_tenant_tarea", "comentario_tarea", ["tenant_id", "tarea_id"])


def _get_tables():
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol", "rol_permiso"))
    return (
        sa.Table("permiso", meta),
        sa.Table("rol", meta),
        sa.Table("rol_permiso", meta),
    )


def _seed_permisos() -> None:
    permiso_tbl, rol_tbl, rp_tbl = _get_tables()
    conn = op.get_bind()

    for perm_data in PERMISOS:
        exists = conn.execute(
            permiso_tbl.select().where(permiso_tbl.c.codigo == perm_data["codigo"])
        ).first()
        if exists is not None:
            continue

        permiso_id = str(uuid.uuid4())
        conn.execute(
            permiso_tbl.insert().values(
                id=permiso_id,
                codigo=perm_data["codigo"],
                descripcion=perm_data["descripcion"],
                modulo=perm_data["modulo"],
                tenant_id=None,
            )
        )

        for rol_name in perm_data["roles"]:
            rol_row = conn.execute(
                rol_tbl.select().where(
                    rol_tbl.c.nombre == rol_name,
                    rol_tbl.c.tenant_id.is_(None),
                )
            ).first()
            if rol_row is None:
                continue
            rol_data = dict(rol_row._mapping)
            conn.execute(
                rp_tbl.insert().values(
                    id=str(uuid.uuid4()),
                    rol_id=rol_data["id"],
                    permiso_id=permiso_id,
                    tenant_id=None,
                )
            )


def _remove_permisos() -> None:
    permiso_tbl, _rol_tbl, rp_tbl = _get_tables()
    conn = op.get_bind()

    for perm_data in PERMISOS:
        perm_row = conn.execute(
            permiso_tbl.select().where(permiso_tbl.c.codigo == perm_data["codigo"])
        ).first()
        if perm_row is None:
            continue
        perm_data_row = dict(perm_row._mapping)
        conn.execute(
            rp_tbl.delete().where(rp_tbl.c.permiso_id == perm_data_row["id"])
        )
        conn.execute(
            permiso_tbl.delete().where(permiso_tbl.c.id == perm_data_row["id"])
        )
