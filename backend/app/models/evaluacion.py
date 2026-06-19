import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Evaluacion(BaseModelMixin, Base):
    __tablename__ = "evaluacion"

    __table_args__ = (
        sa.Index("ix_evaluacion_tenant_materia", "tenant_id", "materia_id"),
        sa.Index("ix_evaluacion_tenant_cohorte", "tenant_id", "cohorte_id"),
        sa.Index("ix_evaluacion_tenant_estado", "tenant_id", "estado"),
    )

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False,
    )
    tipo: Mapped[str] = mapped_column(
        sa.String(20), nullable=False,
    )
    instancia: Mapped[str] = mapped_column(
        sa.String(255), nullable=False,
    )
    dias_disponibles: Mapped[int] = mapped_column(
        sa.Integer, nullable=False,
    )
    cupos_por_dia: Mapped[int] = mapped_column(
        sa.Integer, nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        sa.String(20), default="Activa", server_default=sa.text("'Activa'"), nullable=False,
    )
