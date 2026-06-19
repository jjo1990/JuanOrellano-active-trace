import { z } from 'zod'

export interface Carrera {
  id: string
  codigo: string
  nombre: string
  activa: boolean
}

export interface Cohorte {
  id: string
  nombre: string
  anio_inicio: number
  vigencia_desde: string
  vigencia_hasta?: string
  activa: boolean
}

export interface UsuarioTenant {
  id: string
  nombre: string
  email: string
  identificacion_fiscal?: string
  roles: string[]
  banco?: string
  cbu?: string
  alias_cbu?: string
  regional?: string
  modalidad_facturacion?: string
  activo: boolean
}

export interface AuditoriaEntry {
  id: string
  fecha: string
  usuario_id: string
  usuario_nombre?: string
  materia_id?: string
  materia_nombre?: string
  tipo_accion: string
  registros_afectados: number
  ip?: string
  user_agent?: string
}

export interface AuditoriaFilters {
  fecha_desde?: string
  fecha_hasta?: string
  materia_id?: string
  usuario_id?: string
  tipo_accion?: string
  ip?: string
}

export interface AccionesPorDiaItem {
  fecha: string
  cantidad: number
}

export interface EstadoComunicacionesItem {
  docente_id: string
  docente_nombre: string
  materia_id: string
  materia_nombre: string
  pendientes: number
  enviados: number
  fallidos: number
  cancelados: number
}

export interface InteraccionesItem {
  docente_id: string
  docente_nombre: string
  materia_id: string
  materia_nombre: string
  analisis_desempeno: number
  vista_previa: number
  importaciones: number
  envios: number
  limpieza_datos: number
  config_umbral: number
  emails_generados: number
  lotes_procesados: number
}

export const carreraSchema = z.object({
  codigo: z.string().min(1, 'El código es requerido'),
  nombre: z.string().min(1, 'El nombre es requerido'),
})

export type CarreraFormValues = z.infer<typeof carreraSchema>

export const cohorteSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  anio_inicio: z.number().min(2000, 'El año debe ser mayor a 2000'),
  vigencia_desde: z.string().min(1, 'La fecha desde es requerida'),
  vigencia_hasta: z.string().optional(),
})

export type CohorteFormValues = z.infer<typeof cohorteSchema>

export const usuarioSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  email: z.string().email('Email inválido'),
  identificacion_fiscal: z.string().optional(),
  roles: z.array(z.string()).min(1, 'Al menos un rol requerido'),
  banco: z.string().optional(),
  cbu: z.string().optional(),
  alias_cbu: z.string().optional(),
  regional: z.string().optional(),
  modalidad_facturacion: z.string().optional(),
})

export type UsuarioFormValues = z.infer<typeof usuarioSchema>
