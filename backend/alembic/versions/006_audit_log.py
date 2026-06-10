"""C-05: audit_log table, append-only trigger, impersonacion:usar seed

Revision ID: 006
Revises: 005
Create Date: 2026-06-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_audit_log_table()
    _create_append_only_trigger()
    _seed_impersonacion_permiso()


def downgrade() -> None:
    _remove_seed_data()
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log;")
    op.execute("DROP FUNCTION IF EXISTS fn_audit_log_append_only();")
    op.drop_table("audit_log")


# ── helpers ──────────────────────────────────────────────────────────────


def _create_audit_log_table() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("fecha_hora", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("impersonado_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), nullable=True),
        sa.Column("accion", sa.String(100), nullable=False),
        sa.Column("detalle", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("filas_afectadas", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def _create_append_only_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION fn_audit_log_append_only()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log es append-only: no se permiten UPDATE ni DELETE';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_log_append_only
        BEFORE UPDATE OR DELETE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION fn_audit_log_append_only();
        """
    )


def _seed_impersonacion_permiso() -> None:
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol", "rol_permiso"))
    permiso_tbl = sa.Table("permiso", meta)
    rol_tbl = sa.Table("rol", meta)
    rp_tbl = sa.Table("rol_permiso", meta)

    import uuid

    pid = str(uuid.uuid4())
    conn.execute(
        permiso_tbl.insert().values(
            id=pid,
            codigo="impersonacion:usar",
            descripcion="Suplantar a otro usuario para diagnóstico",
            modulo="auth",
            tenant_id=None,
        )
    )

    roles = conn.execute(
        rol_tbl.select().where(rol_tbl.c.nombre.in_(["ADMIN", "COORDINADOR"]))
    ).fetchall()

    for rol in roles:
        conn.execute(
            rp_tbl.insert().values(
                id=str(uuid.uuid4()),
                rol_id=rol._mapping["id"],
                permiso_id=pid,
                tenant_id=None,
            )
        )


def _remove_seed_data() -> None:
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol_permiso"))
    permiso_tbl = sa.Table("permiso", meta)
    rp_tbl = sa.Table("rol_permiso", meta)

    conn.execute(
        rp_tbl.delete().where(
            rp_tbl.c.permiso_id.in_(
                sa.select(permiso_tbl.c.id).where(
                    permiso_tbl.c.codigo == "impersonacion:usar"
                )
            )
        )
    )
    conn.execute(
        permiso_tbl.delete().where(
            permiso_tbl.c.codigo == "impersonacion:usar"
        )
    )
