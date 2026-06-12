import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.fields import EncryptedField
from app.models.mixins import BaseModelMixin


class EntradaPadron(BaseModelMixin, Base):
    __tablename__ = "entrada_padron"

    __table_args__ = (
        sa.Index("ix_entrada_padron_version", "version_id"),
        sa.Index("ix_entrada_padron_tenant", "tenant_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("version_padron.id"), nullable=False,
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=True,
    )
    nombre: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    email_encrypted: Mapped[str | None] = mapped_column(
        sa.String(512), nullable=True,
    )
    email = EncryptedField()
    comision: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    regional: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
