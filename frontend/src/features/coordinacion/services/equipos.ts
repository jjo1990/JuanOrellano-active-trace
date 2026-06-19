import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  EquipoEntry,
  EquipoFilters,
} from '@/features/coordinacion/types'

export const equiposKeys = {
  all: () => ['equipos'] as const,
  list: (filters: EquipoFilters) => ['equipos', 'list', filters] as const,
  export: () => ['equipos', 'export'] as const,
}

async function fetchEquipos(filters: EquipoFilters): Promise<EquipoEntry[]> {
  const params: Record<string, string> = {}
  if (filters.cohorte_id) params.cohorte_id = filters.cohorte_id
  if (filters.materia_id) params.materia_id = filters.materia_id
  if (filters.search) params.search = filters.search

  const response = await api.get<EquipoEntry[]>('/api/equipos', { params })
  return response.data
}

async function asignarDocentes(data: {
  cohorte_id: string
  asignaciones: Array<{
    docente_id: string
    rol: string
    materia_id: string
    fecha_inicio: string
  }>
}): Promise<{ asignaciones_creadas: number }> {
  const response = await api.post<{ asignaciones_creadas: number }>(
    '/api/equipos/masivo',
    data
  )
  return response.data
}

async function clonarEquipo(data: {
  cohorte_origen_id: string
  cohorte_destino_id: string
}): Promise<{ asignaciones_clonadas: number }> {
  const response = await api.post<{ asignaciones_clonadas: number }>(
    '/api/equipos/clonar',
    data
  )
  return response.data
}

async function updateVigencia(data: {
  asignacion_id: string
  fecha_fin: string
}): Promise<EquipoEntry> {
  const response = await api.put<EquipoEntry>(
    `/api/equipos/${data.asignacion_id}`,
    { fecha_fin: data.fecha_fin }
  )
  return response.data
}

async function exportEquipos(): Promise<Blob> {
  const response = await api.get('/api/equipos/export', {
    responseType: 'blob',
  })
  return response.data as Blob
}

export function useEquipos(filters: EquipoFilters) {
  return useQuery({
    queryKey: equiposKeys.list(filters),
    queryFn: () => fetchEquipos(filters),
  })
}

export function useAsignarDocentes() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: asignarDocentes,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: equiposKeys.all() })
    },
  })
}

export function useClonarEquipo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: clonarEquipo,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: equiposKeys.all() })
    },
  })
}

export function useUpdateVigencia() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateVigencia,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: equiposKeys.all() })
    },
  })
}

export function useExportEquipos() {
  return useMutation({
    mutationFn: () => exportEquipos(),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `equipos-${new Date().toISOString().slice(0, 10)}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
    },
  })
}
