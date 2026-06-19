import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PanelFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    materia_id: uuid.UUID | None = None
    usuario_id: uuid.UUID | None = None
    limite: int = Field(default=200, ge=1, le=1000)


class AccionesPorDia(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    accion: str
    cantidad: int


class EstadoComunicacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: uuid.UUID
    estado: str
    cantidad: int


class InteraccionDocenteMateria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    docente_id: uuid.UUID
    materia_id: uuid.UUID | None
    accion: str
    cantidad: int


class UltimaAccion(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    fecha_hora: datetime
    actor_id: uuid.UUID
    materia_id: uuid.UUID | None = None
    accion: str
    filas_afectadas: int = 0
    ip: str | None = None
    user_agent: str | None = None
    detalle: dict | None = None


class PanelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    acciones_por_dia: list[AccionesPorDia]
    estado_comunicaciones: list[EstadoComunicacion]
    interacciones_docente_materia: list[InteraccionDocenteMateria]
    ultimas_acciones: list[UltimaAccion]


class LogFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    materia_id: uuid.UUID | None = None
    usuario_id: uuid.UUID | None = None
    accion: str | None = None
    limite: int = Field(default=200, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class LogEntryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    fecha_hora: datetime
    actor_id: uuid.UUID
    materia_id: uuid.UUID | None = None
    accion: str
    filas_afectadas: int = 0
    ip: str | None = None
    user_agent: str | None = None
    detalle: dict | None = None


class LogListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[LogEntryResponse]
    limite: int
    offset: int
    total: int
