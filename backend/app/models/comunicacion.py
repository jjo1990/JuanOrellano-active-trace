import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import Boolean, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.fields import EncryptedField
from app.models.mixins import BaseModelMixin


class Comunicacion(BaseModelMixin, Base):
    __tablename__ = "comunicacion"

    __table_args__ = (
        sa.CheckConstraint(
            "estado IN ('Pendiente', 'Enviando', 'Enviado', 'Error', 'Cancelado')",
            name="ck_comunicacion_estado",
        ),
    )

    enviado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    destinatario_encrypted = mapped_column(String(512), nullable=False)
    destinatario = EncryptedField()
    asunto: Mapped[str] = mapped_column(String(500), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20),
        default="Pendiente",
        server_default="Pendiente",
        nullable=False,
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    lote_aprobado: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=sa.false(), nullable=False,
    )
    enviado_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
