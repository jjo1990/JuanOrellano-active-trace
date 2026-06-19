import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GuardiaCreateRequest(BaseModel):
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    asignacion_id: uuid.UUID
    dia: str
    horario: str
    estado: str = "Pendiente"
    comentarios: str | None = None

    model_config = ConfigDict(extra="forbid")


class GuardiaUpdateRequest(BaseModel):
    estado: str | None = None
    horario: str | None = None
    comentarios: str | None = None

    model_config = ConfigDict(extra="forbid")


class GuardiaResponse(BaseModel):
    id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    asignacion_id: uuid.UUID
    dia: str
    horario: str
    estado: str
    comentarios: str | None = None
    creada_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
