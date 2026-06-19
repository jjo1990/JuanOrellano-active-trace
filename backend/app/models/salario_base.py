import enum
import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class RolSalario(str, enum.Enum):
    PROFESOR = "PROFESOR"
    TUTOR = "TUTOR"
    NEXO = "NEXO"
    COORDINADOR = "COORDINADOR"


class SalarioBase(BaseModelMixin, Base):
    __tablename__ = "salario_base"

    __table_args__ = (
        sa.Index("ix_salario_base_tenant_rol", "tenant_id", "rol"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    rol: Mapped[RolSalario] = mapped_column(
        sa.Enum(RolSalario, name="rol_salario_enum", create_type=True), nullable=False,
    )
    monto: Mapped[float] = mapped_column(sa.Numeric(12, 2), nullable=False)
    desde: Mapped[date] = mapped_column(sa.Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
