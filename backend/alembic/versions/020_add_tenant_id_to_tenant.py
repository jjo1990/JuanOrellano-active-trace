"""add tenant_id column to tenant table

La tabla tenant fue creada antes de que BaseModelMixin incluyera tenant_id.
El mixin lo heredan todos los modelos, pero la columna no existe en tenant.

Revision ID: 020
Revises: 019
Create Date: 2026-06-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "020"
down_revision: Union[str, None] = "019"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tenant",
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenant.id"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenant", "tenant_id")
