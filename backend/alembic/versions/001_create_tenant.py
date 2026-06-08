"""create tenant table

Revision ID: 001
Revises:
Create Date: 2026-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column(
            "config", JSONB, nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "estado", sa.String(50), nullable=False,
            server_default=sa.text("'activo'"),
        ),
        sa.Column(
            "created_at", sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "deleted_at", sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    op.create_index("ix_tenant_slug", "tenant", ["slug"], unique=True)
    op.create_index("ix_tenant_estado", "tenant", ["estado"])


def downgrade() -> None:
    op.drop_index("ix_tenant_estado")
    op.drop_index("ix_tenant_slug")
    op.drop_table("tenant")
