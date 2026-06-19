import { z } from 'zod'

export interface Alumno {
  id: string
  nombre: string
  apellido: string
  email: string
  legajo: string
  comision_id?: string
  comision_nombre?: string
}

export interface Actividad {
  id: string
  nombre: string
  tipo: string
  peso?: number
}

export interface Calificacion {
  id: string
  alumno_id: string
  actividad_id: string
  nota: number
  estado: string
  comentario?: string
  alumno_nombre?: string
  actividad_nombre?: string
}

export interface Umbral {
  materia_id: string
  porcentaje: number
  actualizado_por?: string
  actualizado_en?: string
}

export type EstadoEnvio =
  | 'Pendiente'
  | 'Enviando'
  | 'Enviado'
  | 'Error'
  | 'Cancelado'

export type EstadoAlumno = 'Atrasado' | 'Al día' | 'Sin datos'

export interface ComunicacionEnvio {
  id: string
  lote_id: string
  alumno_id: string
  alumno_nombre: string
  email: string
  estado: EstadoEnvio
  error_motivo?: string
  enviado_en?: string
}

export interface ComunicacionLote {
  id: string
  materia_id: string
  plantilla_id: string
  estado: EstadoEnvio
  total_destinatarios: number
  enviados: number
  errores: number
  creado_en: string
}

export interface ImportPreview {
  alumnos: Alumno[]
  actividades: Actividad[]
  calificaciones_preview: Calificacion[]
}

export interface ImportResult {
  importacion_id: string
  calificaciones_importadas: number
  actividades_detectadas: number
  alumnos_detectados: number
}

export interface Atrasado {
  alumno_id: string
  alumno_nombre: string
  actividades_pendientes: number
  nota_promedio: number
  estado: EstadoAlumno
}

export interface RankingEntry {
  alumno_id: string
  alumno_nombre: string
  aprobadas: number
  promedio: number
}

export interface NotaFinal {
  alumno_id: string
  alumno_nombre: string
  nota_final: number
  estado: 'Aprobado' | 'Desaprobado'
}

export interface TpSinCorregir {
  alumno_id: string
  alumno_nombre: string
  actividad_id: string
  actividad_nombre: string
  fecha_entrega?: string
  estado: string
}

export interface MonitorEntry {
  alumno_id: string
  alumno_nombre: string
  email: string
  comision_id: string
  comision_nombre: string
  actividades_completadas: number
  actividades_totales: number
  estado_general: EstadoAlumno
  materias: MonitorMateriaItem[]
}

export interface MonitorMateriaItem {
  materia_id: string
  materia_nombre: string
  estado: EstadoAlumno
}

export interface MonitorFilters {
  materia_id?: string
  comision_id?: string
  search?: string
}

export interface MessagePreview {
  asunto: string
  cuerpo: string
  destinatarios: Alumno[]
  cantidad: number
}

export interface SendRequest {
  materia_id: string
  plantilla_id: string
  destinatarios: string[]
}

export interface SendResult {
  lote_id: string
  total: number
  estado: EstadoEnvio
}

export const umbralSchema = z.object({
  porcentaje: z
    .number()
    .min(0, 'El umbral debe estar entre 0 y 100')
    .max(100, 'El umbral debe estar entre 0 y 100'),
})

export type UmbralFormValues = z.infer<typeof umbralSchema>

export const importSchema = z.object({
  materia_id: z.string().min(1, 'Seleccioná una materia'),
})

export type ImportFormValues = z.infer<typeof importSchema>

export const comunicacionSchema = z.object({
  plantilla_id: z.string().min(1, 'Seleccioná una plantilla'),
  destinatarios: z
    .array(z.string())
    .min(1, 'Seleccioná al menos un destinatario'),
})

export type ComunicacionFormValues = z.infer<typeof comunicacionSchema>
