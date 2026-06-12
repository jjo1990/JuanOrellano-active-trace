import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CalificacionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    entrada_padron_id: uuid.UUID
    materia_id: uuid.UUID
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    origen: str
    importado_at: datetime
    aprobado: bool


class UmbralMateriaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    umbral_pct: int
    valores_aprobatorios: list[str]


class UmbralMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    umbral_pct: int = Field(ge=0, le=100)
    valores_aprobatorios: list[str]


class ColumnaDetectada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    tipo: Literal["numerica", "textual"]
    aprobatorio: bool
    actividad: str


class ImportCalificacionesPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_token: str
    filename: str
    detected_rows: int
    columns: list[ColumnaDetectada]
    actividades: list[dict]
    preview_rows: list[dict]


class ConfirmCalificacionesRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actividades_seleccionadas: list[str]


class ConfirmCalificacionesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calificaciones_count: int
    ignorados_count: int
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    importado_at: datetime


class ImportFinalizacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calificaciones_count: int
    ignorados_count: int
    materia_id: uuid.UUID
