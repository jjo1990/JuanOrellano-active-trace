import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class FechaCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    numero: int
    periodo: str
    fecha: date
    titulo: str


class FechaUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tipo: str | None = None
    numero: int | None = None
    periodo: str | None = None
    fecha: date | None = None
    titulo: str | None = None


class FechaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    numero: int
    periodo: str
    fecha: date
    titulo: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class CalendarioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    calendario: dict[str, list[FechaResponse]]


class CronogramaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    html: str
