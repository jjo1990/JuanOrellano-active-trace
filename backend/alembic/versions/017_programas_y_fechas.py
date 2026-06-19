"""C-17: create programa_materia, fecha_academica

Revision ID: 017
Revises: 016
Create Date: 2026-06-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "017"
down_revision: Union[str, None] = "016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_programa_materia()
    _create_fecha_academica()


def downgrade() -> None:
    op.drop_table("fecha_academica")
    op.drop_table("programa_materia")


def _create_programa_materia() -> None:
    op.create_table(
        "programa_materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column("referencia_archivo", sa.String(1000), nullable=False),
        sa.Column("cargado_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_programa_materia_tenant_materia", "programa_materia", ["tenant_id", "materia_id"])
    op.create_index("ix_programa_materia_tenant_carrera_cohorte", "programa_materia", ["tenant_id", "carrera_id", "cohorte_id"])


def _create_fecha_academica() -> None:
    op.create_table(
        "fecha_academica",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("numero", sa.Integer, nullable=False),
        sa.Column("periodo", sa.String(50), nullable=False),
        sa.Column("fecha", sa.Date, nullable=False),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_fecha_academica_tenant_materia_cohorte", "fecha_academica", ["tenant_id", "materia_id", "cohorte_id"])
    op.create_index("ix_fecha_academica_tenant_fecha", "fecha_academica", ["tenant_id", "fecha"])
