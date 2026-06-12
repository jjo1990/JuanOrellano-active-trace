"""C-09: create version_padron and entrada_padron tables

Revision ID: 009
Revises: 008
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_version_padron()
    _create_entrada_padron()


def downgrade() -> None:
    _drop_entrada_padron()
    _drop_version_padron()


def _create_version_padron() -> None:
    op.create_table(
        "version_padron",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False),
        sa.Column("cargado_por", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column(
            "cargado_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("activa", sa.Boolean, default=True, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "uq_version_padron_activa",
        "version_padron",
        ["materia_id", "cohorte_id", "tenant_id"],
        unique=True,
        postgresql_where=sa.text("activa = true"),
    )


def _create_entrada_padron() -> None:
    op.create_table(
        "entrada_padron",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False),
        sa.Column(
            "version_id", UUID(as_uuid=True), sa.ForeignKey("version_padron.id"), nullable=False,
        ),
        sa.Column("usuario_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("apellidos", sa.String(200), nullable=False),
        sa.Column("email_encrypted", sa.String(512), nullable=True),
        sa.Column("comision", sa.String(50), nullable=True),
        sa.Column("regional", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_entrada_padron_version", "entrada_padron", ["version_id"])
    op.create_index("ix_entrada_padron_tenant", "entrada_padron", ["tenant_id"])


def _drop_version_padron() -> None:
    op.drop_index("uq_version_padron_activa", table_name="version_padron")
    op.drop_table("version_padron")


def _drop_entrada_padron() -> None:
    op.drop_index("ix_entrada_padron_version", table_name="entrada_padron")
    op.drop_index("ix_entrada_padron_tenant", table_name="entrada_padron")
    op.drop_table("entrada_padron")
