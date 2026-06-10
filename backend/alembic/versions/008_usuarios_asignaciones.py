"""C-07: usuarios y asignaciones — alter user, create asignacion

Revision ID: 008
Revises: 007
Create Date: 2026-06-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _alter_user_up()
    _create_asignacion()


def downgrade() -> None:
    _drop_asignacion()
    _alter_user_down()


# ── User ──────────────────────────────────────────────────────────────────


def _alter_user_up() -> None:
    op.add_column("user", sa.Column("nombre", sa.String(100), nullable=False, server_default=""))
    op.add_column("user", sa.Column("apellidos", sa.String(200), nullable=False, server_default=""))
    op.add_column("user", sa.Column("dni_encrypted", sa.String(512), nullable=True))
    op.add_column("user", sa.Column("cuil_encrypted", sa.String(512), nullable=True))
    op.add_column("user", sa.Column("cbu_encrypted", sa.String(512), nullable=True))
    op.add_column("user", sa.Column("alias_cbu_encrypted", sa.String(512), nullable=True))
    op.add_column("user", sa.Column("banco", sa.String(100), nullable=True))
    op.add_column("user", sa.Column("regional", sa.String(100), nullable=True))
    op.add_column("user", sa.Column("legajo", sa.String(50), nullable=True))
    op.add_column("user", sa.Column("legajo_profesional", sa.String(50), nullable=True))
    op.add_column("user", sa.Column("facturador", sa.Boolean, server_default="false", nullable=False))
    op.add_column("user", sa.Column("activo", sa.Boolean, server_default="true", nullable=False))

    # Drop display_name — ya no se usa (reemplazado por nombre + apellidos)
    op.drop_column("user", "display_name")

    # Alembic's alter_column to make nombre/apellidos not nullable after backfill
    op.alter_column("user", "nombre", server_default=None)
    op.alter_column("user", "apellidos", server_default=None)


def _alter_user_down() -> None:
    op.add_column(
        "user",
        sa.Column("display_name", sa.String(255), nullable=False, server_default=""),
    )
    # Populate display_name from nombre + apellidos
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("user",))
    user_tbl = sa.Table("user", meta)
    conn.execute(
        user_tbl.update().values(
            display_name=sa.func.concat(
                sa.func.coalesce(user_tbl.c.nombre, ""),
                " ",
                sa.func.coalesce(user_tbl.c.apellidos, ""),
            ),
        ),
    )
    op.alter_column("user", "display_name", server_default=None)

    op.drop_column("user", "activo")
    op.drop_column("user", "facturador")
    op.drop_column("user", "legajo_profesional")
    op.drop_column("user", "legajo")
    op.drop_column("user", "regional")
    op.drop_column("user", "banco")
    op.drop_column("user", "alias_cbu_encrypted")
    op.drop_column("user", "cbu_encrypted")
    op.drop_column("user", "cuil_encrypted")
    op.drop_column("user", "dni_encrypted")
    op.drop_column("user", "apellidos")
    op.drop_column("user", "nombre")


# ── Asignacion ────────────────────────────────────────────────────────────


def _create_asignacion() -> None:
    op.create_table(
        "asignacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("rol_id", UUID(as_uuid=True), sa.ForeignKey("rol.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=True),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=True),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=True),
        sa.Column("comisiones", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("responsable_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("desde", sa.Date, nullable=False),
        sa.Column("hasta", sa.Date, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_asignacion_tenant_usuario", "asignacion", ["tenant_id", "usuario_id"])
    op.create_index("ix_asignacion_tenant_rol", "asignacion", ["tenant_id", "rol_id"])
    op.create_index("ix_asignacion_tenant_materia", "asignacion", ["tenant_id", "materia_id"])


def _drop_asignacion() -> None:
    op.drop_index("ix_asignacion_tenant_materia")
    op.drop_index("ix_asignacion_tenant_rol")
    op.drop_index("ix_asignacion_tenant_usuario")
    op.drop_table("asignacion")
