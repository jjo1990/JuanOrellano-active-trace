import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Rol(BaseModelMixin, Base):
    __tablename__ = "rol"

    __table_args__ = (
        sa.UniqueConstraint("nombre", "tenant_id", name="uq_rol_nombre_tenant"),
    )

    nombre: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    descripcion: Mapped[str] = mapped_column(sa.String(255), nullable=False)
