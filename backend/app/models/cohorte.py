import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Cohorte(BaseModelMixin, Base):
    __tablename__ = "cohorte"

    __table_args__ = (
        sa.UniqueConstraint("carrera_id", "nombre", "tenant_id", name="uq_cohorte_carrera_nombre"),
    )

    carrera_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    anio: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    vig_desde: Mapped[date] = mapped_column(sa.Date, nullable=False)
    vig_hasta: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    activa: Mapped[bool] = mapped_column(sa.Boolean, server_default="true", default=True, nullable=False)
