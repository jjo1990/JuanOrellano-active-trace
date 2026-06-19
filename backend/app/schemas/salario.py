import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SalarioBaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rol: str = Field(min_length=1, max_length=50)
    monto: float = Field(gt=0)
    desde: date
    hasta: date | None = None


class SalarioBaseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    monto: float | None = Field(default=None, gt=0)
    desde: date | None = None
    hasta: date | None = None


class SalarioBaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    rol: str
    monto: float
    desde: date
    hasta: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SalarioPlusCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    grupo: str = Field(min_length=1, max_length=100)
    rol: str = Field(min_length=1, max_length=50)
    descripcion: str = ""
    monto: float = Field(gt=0)
    desde: date
    hasta: date | None = None


class SalarioPlusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    monto: float | None = Field(default=None, gt=0)
    descripcion: str | None = None
    desde: date | None = None
    hasta: date | None = None


class SalarioPlusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    grupo: str
    rol: str
    descripcion: str
    monto: float
    desde: date
    hasta: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
