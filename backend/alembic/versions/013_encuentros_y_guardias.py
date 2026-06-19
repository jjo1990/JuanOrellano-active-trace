"""C-13: create slot_encuentro, instancia_encuentro, guardia + seed permisos

Revision ID: 013
Revises: 012
Create Date: 2026-06-16
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISOS = [
    {
        "codigo": "encuentros:gestionar",
        "descripcion": "Gestionar encuentros (slots e instancias)",
        "modulo": "encuentros",
        "roles": ["PROFESOR", "COORDINADOR"],
    },
    {
        "codigo": "guardias:registrar",
        "descripcion": "Registrar y gestionar guardias",
        "modulo": "guardias",
        "roles": ["TUTOR", "COORDINADOR", "ADMIN"],
    },
]


def upgrade() -> None:
    _create_slot_encuentro()
    _create_instancia_encuentro()
    _create_guardia()
    _seed_permisos()


def downgrade() -> None:
    _remove_permisos()
    op.drop_table("guardia")
    op.drop_table("instancia_encuentro")
    op.drop_table("slot_encuentro")


def _create_slot_encuentro() -> None:
    op.create_table(
        "slot_encuentro",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignacion.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("hora", sa.Time, nullable=False),
        sa.Column("dia_semana", sa.String(10), nullable=True),
        sa.Column("fecha_inicio", sa.Date, nullable=True),
        sa.Column("cant_semanas", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("fecha_unica", sa.Date, nullable=True),
        sa.Column("meet_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_slot_encuentro_tenant_materia", "slot_encuentro", ["tenant_id", "materia_id"])
    op.create_index("ix_slot_encuentro_tenant_asignacion", "slot_encuentro", ["tenant_id", "asignacion_id"])


def _create_instancia_encuentro() -> None:
    op.create_table(
        "instancia_encuentro",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("slot_id", UUID(as_uuid=True), sa.ForeignKey("slot_encuentro.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("fecha", sa.Date, nullable=False),
        sa.Column("hora", sa.Time, nullable=False),
        sa.Column("titulo", sa.String(255), nullable=False),
        sa.Column("estado", sa.String(20), server_default=sa.text("'Programado'"), nullable=False),
        sa.Column("meet_url", sa.String(500), nullable=True),
        sa.Column("video_url", sa.String(500), nullable=True),
        sa.Column("comentario", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_inst_encuentro_tenant_slot", "instancia_encuentro", ["tenant_id", "slot_id"])
    op.create_index("ix_inst_encuentro_tenant_materia", "instancia_encuentro", ["tenant_id", "materia_id"])
    op.create_index("ix_inst_encuentro_tenant_estado", "instancia_encuentro", ["tenant_id", "estado"])


def _create_guardia() -> None:
    op.create_table(
        "guardia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("asignacion_id", UUID(as_uuid=True), sa.ForeignKey("asignacion.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False),
        sa.Column("dia", sa.String(10), nullable=False),
        sa.Column("horario", sa.String(50), nullable=False),
        sa.Column("estado", sa.String(20), server_default=sa.text("'Pendiente'"), nullable=False),
        sa.Column("comentarios", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_guardia_tenant_materia", "guardia", ["tenant_id", "materia_id"])
    op.create_index("ix_guardia_tenant_asignacion", "guardia", ["tenant_id", "asignacion_id"])


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
