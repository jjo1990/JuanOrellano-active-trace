import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Mensaje(BaseModelMixin, Base):
    __tablename__ = "mensaje"

    __table_args__ = (
        sa.Index("ix_mensaje_tenant_destinatario_leido", "tenant_id", "destinatario_id", "leido"),
        sa.Index("ix_mensaje_tenant_mensaje_padre", "tenant_id", "mensaje_padre_id"),
    )

    remitente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    destinatario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    asunto: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    cuerpo: Mapped[str] = mapped_column(sa.Text, nullable=False)
    mensaje_padre_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("mensaje.id"), nullable=True,
    )
    leido: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false"), default=False,
    )
