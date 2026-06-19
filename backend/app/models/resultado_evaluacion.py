import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ResultadoEvaluacion(BaseModelMixin, Base):
    __tablename__ = "resultado_evaluacion"

    __table_args__ = (
        sa.Index("ix_resultado_eval_tenant_eval", "tenant_id", "evaluacion_id"),
        sa.Index("ix_resultado_eval_tenant_alumno", "tenant_id", "alumno_id"),
        sa.UniqueConstraint("evaluacion_id", "alumno_id", name="uq_resultado_eval_eval_alumno"),
    )

    evaluacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False,
    )
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    nota_final: Mapped[str | None] = mapped_column(
        sa.String(20), nullable=True,
    )
