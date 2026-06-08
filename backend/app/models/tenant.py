import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Tenant(BaseModelMixin, Base):
    __tablename__ = "tenant"

    __table_args__ = (
        sa.Index("ix_tenant_slug", "slug", unique=True),
        sa.Index("ix_tenant_estado", "estado"),
    )

    nombre: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    slug: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    config: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"), default=dict,
    )
    estado: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, server_default=sa.text("'activo'"),
    )
