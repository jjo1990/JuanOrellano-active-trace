import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AcknowledgmentAviso(BaseModelMixin, Base):
    __tablename__ = "acknowledgment_aviso"

    __table_args__ = (
        sa.UniqueConstraint("aviso_id", "usuario_id", name="uq_ack_aviso_usuario"),
        sa.Index("ix_ack_aviso_tenant_aviso", "tenant_id", "aviso_id"),
    )

    aviso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("aviso.id"), nullable=False,
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    confirmado_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(),
    )
