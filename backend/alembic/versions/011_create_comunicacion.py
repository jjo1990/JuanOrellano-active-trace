"""C-12: create comunicacion table

Revision ID: 011
Revises: 010
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_comunicacion()


def downgrade() -> None:
    _drop_comunicacion()


def _create_comunicacion() -> None:
    op.create_table(
        "comunicacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", UUID(as_uuid=True),
            sa.ForeignKey("tenant.id"), nullable=False,
        ),
        sa.Column(
            "enviado_por", UUID(as_uuid=True),
            sa.ForeignKey("user.id"), nullable=False,
        ),
        sa.Column(
            "materia_id", UUID(as_uuid=True),
            sa.ForeignKey("materia.id"), nullable=False,
        ),
        sa.Column("destinatario_encrypted", sa.String(512), nullable=False),
        sa.Column("asunto", sa.String(500), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column(
            "estado",
            sa.String(20),
            nullable=False,
            server_default="Pendiente",
        ),
        sa.Column("lote_id", UUID(as_uuid=True), nullable=True),
        sa.Column(
            "lote_aprobado",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("enviado_at", sa.TIMESTAMP(timezone=True), nullable=True),
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
    op.create_check_constraint(
        "ck_comunicacion_estado",
        "comunicacion",
        "estado IN ('Pendiente', 'Enviando', 'Enviado', 'Error', 'Cancelado')",
    )
    op.create_index(
        "ix_comunicacion_estado",
        "comunicacion",
        ["tenant_id", "estado"],
    )
    op.create_index(
        "ix_comunicacion_lote",
        "comunicacion",
        ["lote_id"],
    )
    op.create_index(
        "ix_comunicacion_materia",
        "comunicacion",
        ["tenant_id", "materia_id"],
    )


def _drop_comunicacion() -> None:
    op.drop_index("ix_comunicacion_materia", table_name="comunicacion")
    op.drop_index("ix_comunicacion_lote", table_name="comunicacion")
    op.drop_index("ix_comunicacion_estado", table_name="comunicacion")
    op.drop_table("comunicacion")
