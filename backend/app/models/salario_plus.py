import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin
from app.models.salario_base import RolSalario


class SalarioPlus(BaseModelMixin, Base):
    __tablename__ = "salario_plus"

    __table_args__ = (
        sa.Index("ix_salario_plus_tenant_grupo_rol", "tenant_id", "grupo", "rol"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    grupo: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    rol: Mapped[RolSalario] = mapped_column(
        sa.Enum(RolSalario, name="rol_salario_enum", create_type=False), nullable=False,
    )
    descripcion: Mapped[str] = mapped_column(sa.String(255), nullable=False, default="")
    monto: Mapped[float] = mapped_column(sa.Numeric(12, 2), nullable=False)
    desde: Mapped[date] = mapped_column(sa.Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
