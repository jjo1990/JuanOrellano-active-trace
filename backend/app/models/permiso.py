import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Permiso(BaseModelMixin, Base):
    __tablename__ = "permiso"

    __table_args__ = (
        sa.UniqueConstraint("codigo", name="uq_permiso_codigo"),
    )

    codigo: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    descripcion: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    modulo: Mapped[str] = mapped_column(sa.String(100), nullable=False)
