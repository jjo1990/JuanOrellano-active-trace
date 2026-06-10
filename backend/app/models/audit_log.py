import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class AuditLog(BaseModelMixin, Base):
    __tablename__ = "audit_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    fecha_hora: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False,
    )
    actor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    impersonado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=True,
    )
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )
    accion: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    detalle: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    filas_afectadas: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, default=0, server_default=sa.text("0"),
    )
    ip: Mapped[str | None] = mapped_column(sa.String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
