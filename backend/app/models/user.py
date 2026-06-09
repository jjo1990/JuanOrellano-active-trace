import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class User(BaseModelMixin, Base):
    __tablename__ = "user"

    __table_args__ = (
        sa.UniqueConstraint("email", "tenant_id", name="uq_user_email_tenant"),
        sa.Index("ix_user_email_tenant", "email", "tenant_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false"), default=False,
    )
    display_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    roles: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=sa.text("'[]'::jsonb"), default=list,
    )
