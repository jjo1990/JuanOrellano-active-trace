import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FacturaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario_id: uuid.UUID
    periodo: str = Field(min_length=7, max_length=7, pattern=r"^\d{4}-\d{2}$")
    detalle: str = ""
    referencia_archivo: str | None = None
    tamano_kb: float | None = Field(default=None, ge=0)


class FacturaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    detalle: str | None = None
    referencia_archivo: str | None = None
    tamano_kb: float | None = Field(default=None, ge=0)


class FacturaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    usuario_id: uuid.UUID
    periodo: str
    detalle: str
    referencia_archivo: str | None = None
    tamano_kb: float | None = None
    estado: str
    cargada_at: datetime | None = None
    abonada_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
