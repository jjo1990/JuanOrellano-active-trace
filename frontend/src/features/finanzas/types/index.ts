import { z } from 'zod'

export interface LiquidacionEntry {
  id: string
  docente_id: string
  docente_nombre: string
  rol: string
  materias: string[]
  salario_base: number
  plus: LiquidacionPlusItem[]
  total: number
  factura: boolean
  segmento: 'general' | 'nexo' | 'factura'
}

export interface LiquidacionPlusItem {
  clave: string
  descripcion: string
  monto: number
}

export interface LiquidacionPeriodo {
  cohorte_id: string
  cohorte_nombre: string
  mes: number
  anio: number
  cerrada: boolean
  fecha_cierre?: string
  total_sin_factura: number
  total_con_factura: number
  entradas: LiquidacionEntry[]
}

export interface LiquidacionCerrada {
  id: string
  cohorte_id: string
  cohorte_nombre: string
  mes: number
  anio: number
  fecha_cierre: string
  total_liquidado: number
  cantidad_docentes: number
}

export interface SalarioBase {
  id: string
  rol: string
  monto: number
  vigencia_desde: string
  vigencia_hasta?: string
  activo: boolean
}

export interface Plus {
  id: string
  clave: string
  rol: string
  descripcion: string
  monto?: number
  porcentaje?: number
  vigencia_desde: string
  vigencia_hasta?: string
  activo: boolean
}

export interface FacturaFilters {
  docente?: string
  estado?: 'Pendiente' | 'Abonada'
  fecha_desde?: string
  fecha_hasta?: string
  search?: string
}

export interface Factura {
  id: string
  docente_id: string
  docente_nombre: string
  periodo: string
  fecha_carga: string
  detalle: string
  archivo_nombre?: string
  archivo_tamano?: number
  estado: 'Pendiente' | 'Abonada'
  fecha_pago?: string
  monto?: number
}

export const salarioBaseSchema = z.object({
  rol: z.string().min(1, 'El rol es requerido'),
  monto: z.number().min(0, 'El monto debe ser mayor o igual a 0'),
  vigencia_desde: z.string().min(1, 'La fecha desde es requerida'),
  vigencia_hasta: z.string().optional(),
})

export type SalarioBaseFormValues = z.infer<typeof salarioBaseSchema>

export const plusSchema = z.object({
  clave: z.string().min(1, 'La clave es requerida'),
  rol: z.string().min(1, 'El rol es requerido'),
  descripcion: z.string().min(1, 'La descripción es requerida'),
  monto: z.number().min(0).optional(),
  porcentaje: z.number().min(0).max(100).optional(),
  vigencia_desde: z.string().min(1, 'La fecha desde es requerida'),
  vigencia_hasta: z.string().optional(),
})

export type PlusFormValues = z.infer<typeof plusSchema>
