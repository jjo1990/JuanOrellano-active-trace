import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class RolPermiso(BaseModelMixin, Base):
    __tablename__ = "rol_permiso"

    __table_args__ = (
        sa.UniqueConstraint("rol_id", "permiso_id", "tenant_id", name="uq_rol_permiso"),
    )

    rol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("rol.id"), nullable=False,
    )
    permiso_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("permiso.id"), nullable=False,
    )
