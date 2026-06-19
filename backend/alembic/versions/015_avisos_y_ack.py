"""C-15: create aviso, acknowledgment_aviso + seed avisos:publicar permiso

Revision ID: 015
Revises: 014
Create Date: 2026-06-16
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISOS = [
    {
        "codigo": "avisos:publicar",
        "descripcion": "Publicar avisos en el tablón institucional",
        "modulo": "avisos",
        "roles": ["COORDINADOR", "ADMIN"],
    },
]


def upgrade() -> None:
    _create_aviso()
    _create_acknowledgment_aviso()
    _seed_permisos()


def downgrade() -> None:
    _remove_permisos()
    op.drop_table("acknowledgment_aviso")
    op.drop_table("aviso")


def _create_aviso() -> None:
    op.create_table(
        "aviso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("alcance", sa.String(20), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=True),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=True),
        sa.Column("rol_destino", sa.String(100), nullable=True),
        sa.Column("severidad", sa.String(20), server_default="Info", nullable=False),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column("inicio_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("orden", sa.Integer, server_default="0", nullable=False),
        sa.Column("activo", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("requiere_ack", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_aviso_tenant_alcance", "aviso", ["tenant_id", "alcance"])
    op.create_index("ix_aviso_tenant_activo", "aviso", ["tenant_id", "activo"])


def _create_acknowledgment_aviso() -> None:
    op.create_table(
        "acknowledgment_aviso",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("aviso_id", UUID(as_uuid=True), sa.ForeignKey("aviso.id"), nullable=False),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("confirmado_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_ack_aviso_usuario", "acknowledgment_aviso", ["aviso_id", "usuario_id"])
    op.create_index("ix_ack_aviso_tenant_aviso", "acknowledgment_aviso", ["tenant_id", "aviso_id"])


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
