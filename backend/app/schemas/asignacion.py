from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AsignacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario_id: uuid.UUID
    rol_id: uuid.UUID
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    comisiones: list[str] = []
    responsable_id: uuid.UUID | None = None
    desde: date
    hasta: date | None = None

    @field_validator("hasta")
    @classmethod
    def _validate_hasta(cls, v, info) -> date | None:
        if v is not None and info.data.get("desde") and v < info.data["desde"]:
            msg = "La fecha 'hasta' debe ser posterior o igual a 'desde'."
            raise ValueError(msg)
        return v


class AsignacionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rol_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: uuid.UUID | None = None
    desde: date | None = None
    hasta: date | None = None


class AsignacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    usuario_id: uuid.UUID
    rol_id: uuid.UUID
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    comisiones: list[str]
    responsable_id: uuid.UUID | None = None
    desde: date
    hasta: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AsignacionListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    rol_id: uuid.UUID | None = None
    vigente: bool | None = None
