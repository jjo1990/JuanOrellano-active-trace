import { z } from 'zod'

export interface EquipoEntry {
  id: string
  docente_id: string
  docente_nombre: string
  rol: string
  materia_id: string
  materia_nombre: string
  comision_id: string
  comision_nombre: string
  cohorte_id: string
  cohorte_nombre: string
  fecha_inicio: string
  fecha_fin?: string
  activo: boolean
}

export interface EquipoFilters {
  cohorte_id?: string
  materia_id?: string
  search?: string
}

export type AvisoScope = 'Global' | 'PorMateria' | 'PorCohorte' | 'PorRol'
export type AvisoSeveridad = 'Baja' | 'Media' | 'Alta' | 'Urgente'

export interface Aviso {
  id: string
  titulo: string
  cuerpo: string
  scope: AvisoScope
  scope_materia_id?: string
  scope_cohorte_id?: string
  scope_rol?: string
  severidad: AvisoSeveridad
  fecha_inicio: string
  fecha_fin: string
  requiere_ack: boolean
  creado_por: string
  creado_en: string
  activo: boolean
}

export interface AvisoAcknowledgment {
  id: string
  aviso_id: string
  usuario_id: string
  usuario_nombre: string
  confirmado_en: string
}

export type TareaEstado = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada'

export interface Tarea {
  id: string
  titulo: string
  descripcion?: string
  estado: TareaEstado
  asignado_por_id: string
  asignado_por_nombre: string
  asignado_a_id: string
  asignado_a_nombre: string
  materia_id?: string
  materia_nombre?: string
  fecha_limite?: string
  creado_en: string
  actualizado_en: string
}

export interface ComentarioTarea {
  id: string
  tarea_id: string
  usuario_id: string
  usuario_nombre: string
  texto: string
  creado_en: string
}

export type TareaTab = 'mis-tareas' | 'administracion'

export interface TareaFilters {
  estado?: TareaEstado
  materia_id?: string
  asignado_a_id?: string
}

export interface MonitorGeneralEntry {
  alumno_id: string
  alumno_nombre: string
  email: string
  comision_id: string
  comision_nombre: string
  actividades_completadas: number
  actividades_totales: number
  estado_general: 'Atrasado' | 'Al día' | 'Sin datos'
  materias: MonitorGeneralMateriaItem[]
}

export interface MonitorGeneralMateriaItem {
  materia_id: string
  materia_nombre: string
  estado: 'Atrasado' | 'Al día' | 'Sin datos'
}

export interface MonitorGeneralFilters {
  materia_id?: string
  comision_id?: string
  regional?: string
  estado?: string
  search?: string
}

export interface MonitorDocenteEntry {
  alumno_id: string
  alumno_nombre: string
  email: string
  materia_id: string
  materia_nombre: string
  comision_id: string
  comision_nombre: string
  actividades_completadas: number
  actividades_totales: number
  estado: 'Atrasado' | 'Al día' | 'Sin datos'
}

export type EncuentroTipo = 'Recurrente' | 'Unico'

export type EncuentroEstado = 'Programada' | 'Realizada' | 'Cancelada'

export interface Encuentro {
  id: string
  dia: string
  hora_inicio: string
  hora_fin: string
  meet_url?: string
  cantidad_semanas?: number
  tipo: EncuentroTipo
  materia_id: string
  materia_nombre?: string
  docente_id: string
  docente_nombre?: string
  cohorte_id: string
  cohorte_nombre?: string
  creado_en: string
}

export interface InstanciaEncuentro {
  id: string
  encuentro_id: string
  fecha: string
  estado: EncuentroEstado
  meet_url?: string
  video_url?: string
  comentario?: string
  creado_en: string
  actualizado_en?: string
}

export interface Guardia {
  id: string
  fecha: string
  materia_id: string
  materia_nombre?: string
  docente_cubierto_id: string
  docente_cubierto_nombre?: string
  tutor_id: string
  tutor_nombre?: string
  comentario?: string
  creado_en: string
}

export interface GuardiaFormValues {
  fecha: string
  materia_id: string
  docente_cubierto_id: string
  comentario?: string
}

export interface Coloquio {
  id: string
  materia_id: string
  materia_nombre?: string
  cohorte_id: string
  cohorte_nombre?: string
  dias: string[]
  cupo_por_turno: number
  activo: boolean
  creado_en: string
}

export interface TurnoColoquio {
  id: string
  coloquio_id: string
  fecha: string
  hora: string
  cupo: number
  reservas: ReservaColoquio[]
  libre: number
  ocupado: number
}

export interface ReservaColoquio {
  id: string
  turno_id: string
  alumno_id: string
  alumno_nombre: string
  alumno_email?: string
  confirmada: boolean
  creado_en: string
}

export interface MetricasColoquiosData {
  total_convocados: number
  reservas_confirmadas: number
  turnos_libres: number
  porcentaje_ocupacion: number
}

export interface Programa {
  id: string
  materia_id: string
  materia_nombre?: string
  carrera_id: string
  carrera_nombre?: string
  cohorte_id: string
  cohorte_nombre?: string
  archivo_nombre: string
  archivo_url?: string
  creado_en: string
}

export interface FechaAcademica {
  id: string
  tipo: 'Parcial' | 'TP' | 'Coloquio' | 'Recuperatorio' | 'Otro'
  numero?: number
  fecha: string
  materia_id: string
  materia_nombre?: string
  cohorte_id: string
  cohorte_nombre?: string
  comentario?: string
}

export type SetupPaso = 1 | 2 | 3 | 4 | 5

export interface SetupWizardState {
  paso_actual: SetupPaso
  cohorte_id: string
  cohorte_nombre: string
  docentes_asignados: AsignacionDocenteItem[]
  padron_importado: boolean
  fechas_configuradas: FechaAcademica[]
  completado: boolean
}

export interface AsignacionDocenteItem {
  docente_id: string
  docente_nombre: string
  rol: string
  materia_id: string
  materia_nombre: string
  fecha_inicio: string
}

export interface DocenteSearchResult {
  id: string
  nombre: string
  email: string
  roles: string[]
}

export const avisoSchema = z.object({
  titulo: z.string().min(1, 'El título es requerido'),
  cuerpo: z.string().min(1, 'El cuerpo es requerido'),
  scope: z.enum(['Global', 'PorMateria', 'PorCohorte', 'PorRol']),
  scope_materia_id: z.string().optional(),
  scope_cohorte_id: z.string().optional(),
  scope_rol: z.string().optional(),
  severidad: z.enum(['Baja', 'Media', 'Alta', 'Urgente']),
  fecha_inicio: z.string().min(1, 'Fecha inicio requerida'),
  fecha_fin: z.string().min(1, 'Fecha fin requerida'),
  requiere_ack: z.boolean(),
})

export type AvisoFormValues = z.infer<typeof avisoSchema>

export const tareaSchema = z.object({
  titulo: z.string().min(1, 'El título es requerido'),
  descripcion: z.string().optional(),
  asignado_a_id: z.string().min(1, 'Seleccioná un docente'),
  materia_id: z.string().optional(),
  fecha_limite: z.string().optional(),
})

export type TareaFormValues = z.infer<typeof tareaSchema>

export const encuentroSchema = z.object({
  dia: z.string().min(1, 'El día es requerido'),
  hora_inicio: z.string().min(1, 'La hora de inicio es requerida'),
  hora_fin: z.string().min(1, 'La hora de fin es requerida'),
  meet_url: z.string().optional(),
  tipo: z.enum(['Recurrente', 'Unico']),
  cantidad_semanas: z.number().optional(),
  materia_id: z.string().min(1, 'La materia es requerida'),
  docente_id: z.string().min(1, 'El docente es requerido'),
  cohorte_id: z.string().min(1, 'La cohorte es requerida'),
})

export type EncuentroFormValues = z.infer<typeof encuentroSchema>

export const convocatoriaSchema = z.object({
  materia_id: z.string().min(1, 'La materia es requerida'),
  cohorte_id: z.string().min(1, 'La cohorte es requerida'),
  dias: z.array(z.string()).min(1, 'Al menos un día requerido'),
  cupo_por_turno: z.number().min(1, 'El cupo debe ser al menos 1'),
})

export type ConvocatoriaFormValues = z.infer<typeof convocatoriaSchema>

export const fechaAcademicaSchema = z.object({
  tipo: z.enum(['Parcial', 'TP', 'Coloquio', 'Recuperatorio', 'Otro']),
  numero: z.number().optional(),
  fecha: z.string().min(1, 'La fecha es requerida'),
  materia_id: z.string().min(1, 'La materia es requerida'),
  cohorte_id: z.string().min(1, 'La cohorte es requerida'),
  comentario: z.string().optional(),
})

export type FechaAcademicaFormValues = z.infer<typeof fechaAcademicaSchema>

export const guardiaSchema = z.object({
  fecha: z.string().min(1, 'La fecha es requerida'),
  materia_id: z.string().min(1, 'La materia es requerida'),
  docente_cubierto_id: z.string().min(1, 'El docente es requerido'),
  comentario: z.string().optional(),
})

export type GuardiaFormValues = z.infer<typeof guardiaSchema>
