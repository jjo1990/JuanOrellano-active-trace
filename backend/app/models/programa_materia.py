import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ProgramaMateria(BaseModelMixin, Base):
    __tablename__ = "programa_materia"

    __table_args__ = (
        sa.Index("ix_programa_materia_tenant_materia", "tenant_id", "materia_id"),
        sa.Index("ix_programa_materia_tenant_carrera_cohorte", "tenant_id", "carrera_id", "cohorte_id"),
    )

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    carrera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False,
    )
    titulo: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    referencia_archivo: Mapped[str] = mapped_column(sa.String(1000), nullable=False)
    cargado_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False,
    )
