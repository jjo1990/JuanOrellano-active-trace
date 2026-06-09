import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class PasswordResetToken(BaseModelMixin, Base):
    __tablename__ = "password_reset_token"

    __table_args__ = (
        sa.Index("ix_password_reset_token_hash", "token_hash", unique=True),
    )

    token_hash: Mapped[str] = mapped_column(
        sa.String(64), nullable=False, unique=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True,
    )
