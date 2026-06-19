import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

# ── Carrera ───────────────────────────────────────────────────────────────


class CarreraCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str
    nombre: str
    activa: bool = True


class CarreraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = None
    nombre: str | None = None
    activa: bool | None = None


class CarreraResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    codigo: str
    nombre: str
    activa: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


# ── Cohorte ───────────────────────────────────────────────────────────────


class CohorteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    carrera_id: uuid.UUID
    nombre: str
    anio: int
    vig_desde: date
    vig_hasta: date | None = None
    activa: bool = True


class CohorteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = None
    anio: int | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None
    activa: bool | None = None


class CohorteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    carrera_id: uuid.UUID
    nombre: str
    anio: int
    vig_desde: date
    vig_hasta: date | None = None
    activa: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


# ── Materia ───────────────────────────────────────────────────────────────


class MateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str
    nombre: str
    grupo_plus: str | None = None
    activa: bool = True


class MateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    codigo: str | None = None
    nombre: str | None = None
    grupo_plus: str | None = None
    activa: bool | None = None


class MateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    codigo: str
    nombre: str
    grupo_plus: str | None = None
    activa: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
