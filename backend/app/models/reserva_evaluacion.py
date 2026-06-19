import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ReservaEvaluacion(BaseModelMixin, Base):
    __tablename__ = "reserva_evaluacion"

    __table_args__ = (
        sa.Index("ix_reserva_eval_tenant_eval", "tenant_id", "evaluacion_id"),
        sa.Index("ix_reserva_eval_tenant_alumno", "tenant_id", "alumno_id"),
        sa.Index("ix_reserva_eval_tenant_estado", "tenant_id", "estado"),
    )

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False,
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    fecha_hora: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        sa.String(20), default="Activa", server_default=sa.text("'Activa'"), nullable=False,
    )
