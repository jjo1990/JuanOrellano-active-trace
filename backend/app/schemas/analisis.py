import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CalificacionItemDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    aprobado: bool


class NotaBajaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actividad: str
    nota: float | None = None
    nota_textual: str | None = None


class AlumnoAtrasadoDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    regional: str | None = None
    actividades_faltantes: list[str] = []
    notas_bajas: list[NotaBajaDTO] = []


class AtrasadosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    total_alumnos: int
    total_atrasados: int
    atrasados: list[AlumnoAtrasadoDTO] = []
    status_info: str | None = None


class RankingEntryDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    regional: str | None = None
    total_actividades: int
    aprobadas: int
    porcentaje: float


class RankingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    total_alumnos: int
    ranking: list[RankingEntryDTO] = []
    status_info: str | None = None


class ReportesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    total_alumnos: int
    total_actividades: int
    aprobacion_general: float
    distribucion_notas: dict[str, int] = {}
    alumnos_al_dia: int
    alumnos_atrasados: int
    actividad_mas_dificil: str | None = None
    actividad_mas_facil: str | None = None
    status_info: str | None = None


class NotaFinalDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    regional: str | None = None
    nota_final: float | None = None
    aprobado_final: bool
    calificaciones: list[CalificacionItemDTO] = []


class NotasFinalesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    notas: list[NotaFinalDTO] = []
    status_info: str | None = None


class EntregaSinCorregirDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    comision: str | None = None
    actividad: str
    fecha_finalizacion: datetime | None = None


class SinCorregirResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    total_sin_corregir: int
    entregas: list[EntregaSinCorregirDTO] = []


class MonitorEntryDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    materia_id: uuid.UUID
    materia_nombre: str
    comision: str | None = None
    regional: str | None = None
    estado: str
    total_actividades: int
    aprobadas: int
    faltantes: int
    ultima_actividad: str | None = None


class MonitorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    estudiantes: list[MonitorEntryDTO] = []


class SeguimientoEntryDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    materia_id: uuid.UUID
    materia_nombre: str
    comision: str | None = None
    regional: str | None = None
    estado: str
    total_actividades: int
    aprobadas: int
    faltantes: int


class SeguimientoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    estudiantes: list[SeguimientoEntryDTO] = []


class RangoFechasDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    desde: date | None = None
    hasta: date | None = None


class AdminMonitorEntryDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    materia_id: uuid.UUID
    materia_nombre: str
    comision: str | None = None
    regional: str | None = None
    estado: str
    total_actividades: int
    aprobadas: int
    faltantes: int


class AdminMonitorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    rango_fechas: RangoFechasDTO | None = None
    estudiantes: list[AdminMonitorEntryDTO] = []
