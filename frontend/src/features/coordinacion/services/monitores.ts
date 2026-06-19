import { useQuery } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  MonitorGeneralEntry,
  MonitorGeneralFilters,
  MonitorDocenteEntry,
} from '@/features/coordinacion/types'

export const monitoresKeys = {
  all: () => ['monitores'] as const,
  general: (filters: MonitorGeneralFilters) =>
    ['monitores', 'general', filters] as const,
  porDocente: (docenteId: string) =>
    ['monitores', 'por-docente', docenteId] as const,
}

async function fetchMonitorGeneral(
  filters: MonitorGeneralFilters
): Promise<MonitorGeneralEntry[]> {
  const params: Record<string, string> = {}
  if (filters.materia_id) params.materia_id = filters.materia_id
  if (filters.comision_id) params.comision_id = filters.comision_id
  if (filters.regional) params.regional = filters.regional
  if (filters.estado) params.estado = filters.estado
  if (filters.search) params.search = filters.search

  const response = await api.get<MonitorGeneralEntry[]>(
    '/api/analisis/monitor',
    { params }
  )
  return response.data
}

async function fetchMonitorPorDocente(
  docenteId: string
): Promise<MonitorDocenteEntry[]> {
  const response = await api.get<MonitorDocenteEntry[]>(
    '/api/analisis/monitor/docente',
    { params: { docente_id: docenteId } }
  )
  return response.data
}

export function useMonitorGeneral(filters: MonitorGeneralFilters) {
  return useQuery({
    queryKey: monitoresKeys.general(filters),
    queryFn: () => fetchMonitorGeneral(filters),
  })
}

export function useMonitorPorDocente(docenteId: string) {
  return useQuery({
    queryKey: monitoresKeys.porDocente(docenteId),
    queryFn: () => fetchMonitorPorDocente(docenteId),
    enabled: !!docenteId,
  })
}
