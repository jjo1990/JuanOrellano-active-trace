"""C-10: create calificacion and umbral_materia tables

Revision ID: 010
Revises: 009
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_calificacion()
    _create_umbral_materia()


def downgrade() -> None:
    _drop_umbral_materia()
    _drop_calificacion()


def _create_calificacion() -> None:
    op.create_table(
        "calificacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
        ),
        sa.Column(
            "entrada_padron_id", UUID(as_uuid=True),
            sa.ForeignKey("entrada_padron.id"), nullable=False,
        ),
        sa.Column(
            "materia_id", UUID(as_uuid=True),
            sa.ForeignKey("materia.id"), nullable=False,
        ),
        sa.Column("actividad", sa.String(200), nullable=False),
        sa.Column("nota_numerica", sa.Numeric(5, 2), nullable=True),
        sa.Column("nota_textual", sa.String(200), nullable=True),
        sa.Column("origen", sa.String(20), nullable=False),
        sa.Column(
            "importado_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
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
        "ix_calificacion_entrada_materia",
        "calificacion",
        ["entrada_padron_id", "materia_id"],
    )
    op.create_index(
        "ix_calificacion_materia",
        "calificacion",
        ["materia_id"],
    )
    op.create_index(
        "ix_calificacion_padron",
        "calificacion",
        ["entrada_padron_id"],
    )
    op.create_check_constraint(
        "ck_calificacion_origen",
        "calificacion",
        "origen IN ('Importado', 'Manual')",
    )


def _create_umbral_materia() -> None:
    op.create_table(
        "umbral_materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
        ),
        sa.Column(
            "asignacion_id", UUID(as_uuid=True),
            sa.ForeignKey("asignacion.id"), nullable=False,
        ),
        sa.Column(
            "materia_id", UUID(as_uuid=True),
            sa.ForeignKey("materia.id"), nullable=False,
        ),
        sa.Column(
            "umbral_pct",
            sa.Integer,
            nullable=False,
            server_default="60",
        ),
        sa.Column(
            "valores_aprobatorios",
            sa.JSON,
            nullable=False,
            server_default=sa.text("'[\"Satisfactorio\", \"Supera lo esperado\"]'::jsonb"),
        ),
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
        "uq_umbral_asignacion_materia",
        "umbral_materia",
        ["asignacion_id", "materia_id", "tenant_id"],
        unique=True,
    )
    op.create_index(
        "ix_umbral_asignacion",
        "umbral_materia",
        ["asignacion_id"],
    )


def _drop_calificacion() -> None:
    op.drop_index("ix_calificacion_entrada_materia", table_name="calificacion")
    op.drop_index("ix_calificacion_materia", table_name="calificacion")
    op.drop_index("ix_calificacion_padron", table_name="calificacion")
    op.drop_table("calificacion")


def _drop_umbral_materia() -> None:
    op.drop_index("uq_umbral_asignacion_materia", table_name="umbral_materia")
    op.drop_index("ix_umbral_asignacion", table_name="umbral_materia")
    op.drop_table("umbral_materia")
