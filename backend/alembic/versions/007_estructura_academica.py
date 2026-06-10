"""C-06: create carrera, cohorte, materia tables with unique constraints

Revision ID: 007
Revises: 006
Create Date: 2026-06-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_carrera()
    _create_cohorte()
    _create_materia()


def downgrade() -> None:
    op.drop_table("materia")
    op.drop_table("cohorte")
    op.drop_table("carrera")


def _create_carrera() -> None:
    op.create_table(
        "carrera",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("activa", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_carrera_codigo_tenant", "carrera", ["codigo", "tenant_id"])


def _create_cohorte() -> None:
    op.create_table(
        "cohorte",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("carrera_id", UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("anio", sa.Integer, nullable=False),
        sa.Column("vig_desde", sa.Date, nullable=False),
        sa.Column("vig_hasta", sa.Date, nullable=True),
        sa.Column("activa", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_cohorte_carrera_nombre", "cohorte", ["carrera_id", "nombre", "tenant_id"])


def _create_materia() -> None:
    op.create_table(
        "materia",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("activa", sa.Boolean, server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_materia_codigo_tenant", "materia", ["codigo", "tenant_id"])
