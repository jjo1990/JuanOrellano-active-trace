import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EvaluacionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str = Field(description="Parcial | TP | Coloquio | Recuperatorio")
    instancia: str
    dias_disponibles: int
    cupos_por_dia: int


class EvaluacionUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str | None = None
    cupos_por_dia: int | None = None
    dias_disponibles: int | None = None


class AlumnoInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    legajo: str | None = None


class ReservaInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    fecha_hora: datetime
    estado: str
    created_at: datetime


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    tipo: str
    instancia: str
    dias_disponibles: int
    cupos_por_dia: int
    estado: str
    created_at: datetime
    total_alumnos: int = 0
    reservas_activas: int = 0
    cupos_libres: int = 0


class EvaluacionDetailResponse(EvaluacionResponse):
    alumnos: list[AlumnoInfo] = []
    reservas: list[ReservaInfo] = []


class ImportAlumnoItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID


class ImportAlumnosRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumnos: list[ImportAlumnoItem]


class ReservaCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluacion_id: uuid.UUID
    fecha_hora: datetime


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    fecha_hora: datetime
    estado: str
    created_at: datetime


class ReservaAgendaResponse(ReservaResponse):
    alumno_nombre: str = ""
    alumno_legajo: str | None = None
    materia_nombre: str = ""
    cohorte_nombre: str = ""


class ResultadoCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    nota_final: str


class ResultadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    evaluacion_id: uuid.UUID
    alumno_id: uuid.UUID
    nota_final: str | None = None
    created_at: datetime
    updated_at: datetime


class ResultadoConsolidadoResponse(ResultadoResponse):
    alumno_nombre: str = ""
    alumno_legajo: str | None = None
    materia_nombre: str = ""
    cohorte_nombre: str = ""
    tipo_evaluacion: str = ""
    instancia: str = ""


class MetricasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_alumnos_cargados: int = 0
    total_instancias_activas: int = 0
    total_reservas_activas: int = 0
    total_notas_registradas: int = 0


class AgendaFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    q: str | None = None


class ResultadosFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    pendientes: bool = False
