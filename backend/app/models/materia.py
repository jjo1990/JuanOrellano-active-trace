import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Materia(BaseModelMixin, Base):
    __tablename__ = "materia"

    __table_args__ = (
        sa.UniqueConstraint("codigo", "tenant_id", name="uq_materia_codigo_tenant"),
    )

    codigo: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    grupo_plus: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    activa: Mapped[bool] = mapped_column(sa.Boolean, server_default="true", default=True, nullable=False)
