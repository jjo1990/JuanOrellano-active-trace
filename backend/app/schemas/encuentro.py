import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InstanciaBase(BaseModel):
    id: uuid.UUID
    slot_id: uuid.UUID | None = None
    materia_id: uuid.UUID
    fecha: date
    hora: time
    titulo: str
    estado: str
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InstanciaResponse(InstanciaBase):
    pass


class InstanciaCreateRequest(BaseModel):
    fecha: date
    hora: time
    titulo: str
    materia_id: uuid.UUID
    asignacion_id: uuid.UUID
    meet_url: str | None = None

    model_config = ConfigDict(extra="forbid")


class InstanciaUpdateRequest(BaseModel):
    estado: str | None = None
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None

    model_config = ConfigDict(extra="forbid")


class SlotCreateRequest(BaseModel):
    titulo: str
    hora: time
    dia_semana: str | None = None
    fecha_inicio: date | None = None
    cant_semanas: int = 0
    fecha_unica: date | None = None
    meet_url: str | None = None
    materia_id: uuid.UUID
    asignacion_id: uuid.UUID

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _validate_mode(self):
        recurrente = self.cant_semanas > 0
        unico = self.fecha_unica is not None

        if not recurrente and not unico:
            raise ValueError("Debe especificar modo recurrente (cant_semanas >= 1 + dia_semana + fecha_inicio) o modo unico (fecha_unica).")

        if recurrente:
            if self.cant_semanas < 1:
                raise ValueError("cant_semanas debe ser >= 1 en modo recurrente.")
            if self.dia_semana is None:
                raise ValueError("dia_semana es requerido en modo recurrente.")
            if self.fecha_inicio is None:
                raise ValueError("fecha_inicio es requerido en modo recurrente.")

        return self


class SlotBase(BaseModel):
    id: uuid.UUID
    titulo: str
    hora: time
    dia_semana: str | None = None
    fecha_inicio: date | None = None
    cant_semanas: int = 0
    fecha_unica: date | None = None
    meet_url: str | None = None
    materia_id: uuid.UUID
    asignacion_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SlotResponse(SlotBase):
    instancias: list[InstanciaResponse] = []


class AulaVirtualResponse(BaseModel):
    html: str

    model_config = ConfigDict(extra="forbid")


class AdminEncuentrosFilterParams(BaseModel):
    materia_id: uuid.UUID | None = None
    estado: str | None = None
    fecha_desde: date | None = None
    fecha_hasta: date | None = None

    model_config = ConfigDict(extra="forbid")
