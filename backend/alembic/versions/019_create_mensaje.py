"""C-20: create mensaje table

Revision ID: 019
Revises: 018
Create Date: 2026-06-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "019"
down_revision: Union[str, None] = "018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mensaje",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("remitente_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("destinatario_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("asunto", sa.String(255), nullable=False),
        sa.Column("cuerpo", sa.Text, nullable=False),
        sa.Column("mensaje_padre_id", UUID(as_uuid=True), sa.ForeignKey("mensaje.id"), nullable=True),
        sa.Column("leido", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_mensaje_tenant_destinatario_leido", "mensaje",
        ["tenant_id", "destinatario_id", "leido"],
    )
    op.create_index(
        "ix_mensaje_tenant_mensaje_padre", "mensaje",
        ["tenant_id", "mensaje_padre_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_mensaje_tenant_mensaje_padre")
    op.drop_index("ix_mensaje_tenant_destinatario_leido")
    op.drop_table("mensaje")
