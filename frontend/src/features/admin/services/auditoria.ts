import { useQuery } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  AuditoriaEntry,
  AuditoriaFilters,
  AccionesPorDiaItem,
  EstadoComunicacionesItem,
  InteraccionesItem,
} from '@/features/admin/types'

export const auditoriaKeys = {
  all: ['auditoria'] as const,
  log: (filters: AuditoriaFilters, page?: number, sort?: string, order?: string) =>
    ['auditoria', 'log', { ...filters, page, sort, order }] as const,
  accionesPorDia: (filters: AuditoriaFilters) =>
    ['auditoria', 'acciones-por-dia', filters] as const,
  estadoComunicaciones: (filters: AuditoriaFilters) =>
    ['auditoria', 'estado-comunicaciones', filters] as const,
  interacciones: (filters: AuditoriaFilters) =>
    ['auditoria', 'interacciones', filters] as const,
  ultimasAcciones: (filters: AuditoriaFilters) =>
    ['auditoria', 'ultimas-acciones', filters] as const,
}

async function fetchAuditoriaLog(
  filters: AuditoriaFilters,
  page?: number,
  sort?: string,
  order?: string
): Promise<{ items: AuditoriaEntry[]; total: number }> {
  const params: Record<string, string | number> = {}
  if (filters.fecha_desde) params.fecha_desde = filters.fecha_desde
  if (filters.fecha_hasta) params.fecha_hasta = filters.fecha_hasta
  if (filters.materia_id) params.materia_id = filters.materia_id
  if (filters.usuario_id) params.usuario_id = filters.usuario_id
  if (filters.tipo_accion) params.tipo_accion = filters.tipo_accion
  if (filters.ip) params.ip = filters.ip
  if (page) params.page = page
  if (sort) params.sort = sort
  if (order) params.order = order
  const response = await api.get<{ items: AuditoriaEntry[]; total: number }>(
    '/api/auditoria/log',
    { params }
  )
  return response.data
}

async function fetchAccionesPorDia(
  filters: AuditoriaFilters
): Promise<AccionesPorDiaItem[]> {
  const params: Record<string, string> = {}
  if (filters.fecha_desde) params.fecha_desde = filters.fecha_desde
  if (filters.fecha_hasta) params.fecha_hasta = filters.fecha_hasta
  const response = await api.get<AccionesPorDiaItem[]>(
    '/api/auditoria/acciones-por-dia',
    { params }
  )
  return response.data
}

async function fetchEstadoComunicaciones(
  filters: AuditoriaFilters
): Promise<EstadoComunicacionesItem[]> {
  const params: Record<string, string> = {}
  if (filters.materia_id) params.materia_id = filters.materia_id
  if (filters.usuario_id) params.usuario_id = filters.usuario_id
  const response = await api.get<EstadoComunicacionesItem[]>(
    '/api/auditoria/estado-comunicaciones',
    { params }
  )
  return response.data
}

async function fetchInteracciones(
  filters: AuditoriaFilters
): Promise<InteraccionesItem[]> {
  const params: Record<string, string> = {}
  if (filters.fecha_desde) params.fecha_desde = filters.fecha_desde
  if (filters.fecha_hasta) params.fecha_hasta = filters.fecha_hasta
  if (filters.materia_id) params.materia_id = filters.materia_id
  const response = await api.get<InteraccionesItem[]>(
    '/api/auditoria/interacciones',
    { params }
  )
  return response.data
}

async function fetchUltimasAcciones(
  filters: AuditoriaFilters,
  limit = 200
): Promise<AuditoriaEntry[]> {
  const params: Record<string, string | number> = { limit }
  if (filters.fecha_desde) params.fecha_desde = filters.fecha_desde
  if (filters.fecha_hasta) params.fecha_hasta = filters.fecha_hasta
  if (filters.materia_id) params.materia_id = filters.materia_id
  if (filters.usuario_id) params.usuario_id = filters.usuario_id
  if (filters.tipo_accion) params.tipo_accion = filters.tipo_accion
  const response = await api.get<AuditoriaEntry[]>(
    '/api/auditoria/ultimas-acciones',
    { params }
  )
  return response.data
}

export function useAuditoriaLog(
  filters: AuditoriaFilters,
  page?: number,
  sort?: string,
  order?: string
) {
  return useQuery({
    queryKey: auditoriaKeys.log(filters, page, sort, order),
    queryFn: () => fetchAuditoriaLog(filters, page, sort, order),
  })
}

export function useAccionesPorDia(filters: AuditoriaFilters) {
  return useQuery({
    queryKey: auditoriaKeys.accionesPorDia(filters),
    queryFn: () => fetchAccionesPorDia(filters),
  })
}

export function useEstadoComunicaciones(filters: AuditoriaFilters) {
  return useQuery({
    queryKey: auditoriaKeys.estadoComunicaciones(filters),
    queryFn: () => fetchEstadoComunicaciones(filters),
  })
}

export function useInteracciones(filters: AuditoriaFilters) {
  return useQuery({
    queryKey: auditoriaKeys.interacciones(filters),
    queryFn: () => fetchInteracciones(filters),
  })
}

export function useUltimasAcciones(filters: AuditoriaFilters) {
  return useQuery({
    queryKey: auditoriaKeys.ultimasAcciones(filters),
    queryFn: () => fetchUltimasAcciones(filters),
  })
}
