import { useQuery } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Atrasado,
  RankingEntry,
  NotaFinal,
  TpSinCorregir,
  MonitorEntry,
  MonitorFilters,
} from '@/features/academico/types'

export const analisisKeys = {
  all: ['analisis'] as const,
  atrasados: (materiaId: string) => ['analisis', 'atrasados', materiaId] as const,
  ranking: (materiaId: string) => ['analisis', 'ranking', materiaId] as const,
  notasFinales: (materiaId: string) =>
    ['analisis', 'notas-finales', materiaId] as const,
  tpsSinCorregir: (materiaId: string) =>
    ['analisis', 'tps-sin-corregir', materiaId] as const,
  monitor: (filters: MonitorFilters) =>
    ['analisis', 'monitor', filters] as const,
}

async function fetchAtrasados(materiaId: string): Promise<Atrasado[]> {
  const response = await api.get<Atrasado[]>('/api/analisis/atrasados', {
    params: { materia_id: materiaId },
  })
  return response.data
}

async function fetchRanking(materiaId: string): Promise<RankingEntry[]> {
  const response = await api.get<RankingEntry[]>('/api/analisis/ranking', {
    params: { materia_id: materiaId },
  })
  return response.data
}

async function fetchNotasFinales(materiaId: string): Promise<NotaFinal[]> {
  const response = await api.get<NotaFinal[]>('/api/analisis/notas-finales', {
    params: { materia_id: materiaId },
  })
  return response.data
}

async function fetchTpsSinCorregir(materiaId: string): Promise<TpSinCorregir[]> {
  const response = await api.get<TpSinCorregir[]>(
    '/api/analisis/tps-sin-corregir',
    { params: { materia_id: materiaId } }
  )
  return response.data
}

async function fetchMonitor(filters: MonitorFilters): Promise<MonitorEntry[]> {
  const params: Record<string, string> = {}
  if (filters.materia_id) params.materia_id = filters.materia_id
  if (filters.comision_id) params.comision_id = filters.comision_id
  if (filters.search) params.search = filters.search

  const response = await api.get<MonitorEntry[]>('/api/analisis/monitor', {
    params,
  })
  return response.data
}

export function useAtrasados(materiaId: string) {
  return useQuery({
    queryKey: analisisKeys.atrasados(materiaId),
    queryFn: () => fetchAtrasados(materiaId),
    enabled: !!materiaId,
  })
}

export function useRanking(materiaId: string) {
  return useQuery({
    queryKey: analisisKeys.ranking(materiaId),
    queryFn: () => fetchRanking(materiaId),
    enabled: !!materiaId,
  })
}

export function useNotasFinales(materiaId: string) {
  return useQuery({
    queryKey: analisisKeys.notasFinales(materiaId),
    queryFn: () => fetchNotasFinales(materiaId),
    enabled: !!materiaId,
  })
}

export function useTpsSinCorregir(materiaId: string) {
  return useQuery({
    queryKey: analisisKeys.tpsSinCorregir(materiaId),
    queryFn: () => fetchTpsSinCorregir(materiaId),
    enabled: !!materiaId,
  })
}

export function useMonitor(filters: MonitorFilters) {
  return useQuery({
    queryKey: analisisKeys.monitor(filters),
    queryFn: () => fetchMonitor(filters),
  })
}
