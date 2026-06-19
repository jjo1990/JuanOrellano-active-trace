import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class FechaAcademica(BaseModelMixin, Base):
    __tablename__ = "fecha_academica"

    __table_args__ = (
        sa.Index("ix_fecha_academica_tenant_materia_cohorte", "tenant_id", "materia_id", "cohorte_id"),
        sa.Index("ix_fecha_academica_tenant_fecha", "tenant_id", "fecha"),
    )

    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False,
    )
    tipo: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    numero: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    periodo: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    fecha: Mapped[date] = mapped_column(sa.Date, nullable=False)
    titulo: Mapped[str] = mapped_column(sa.String(500), nullable=False)
