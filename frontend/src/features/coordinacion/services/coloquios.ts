import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Coloquio,
  ConvocatoriaFormValues,
  TurnoColoquio,
  MetricasColoquiosData,
} from '@/features/coordinacion/types'

export const coloquiosKeys = {
  all: () => ['coloquios'] as const,
  list: () => ['coloquios', 'list'] as const,
  turnos: (coloquioId: string) =>
    ['coloquios', 'turnos', coloquioId] as const,
  metricas: () => ['coloquios', 'metricas'] as const,
}

async function fetchColoquios(): Promise<Coloquio[]> {
  const response = await api.get<Coloquio[]>('/api/coloquios')
  return response.data
}

async function createColoquio(
  data: ConvocatoriaFormValues
): Promise<Coloquio> {
  const response = await api.post<Coloquio>('/api/coloquios', data)
  return response.data
}

async function importarAlumnos(
  coloquioId: string
): Promise<{ alumnos_importados: number }> {
  const response = await api.post<{ alumnos_importados: number }>(
    `/api/coloquios/${coloquioId}/importar-alumnos`
  )
  return response.data
}

async function fetchTurnos(coloquioId: string): Promise<TurnoColoquio[]> {
  const response = await api.get<TurnoColoquio[]>(
    `/api/coloquios/${coloquioId}/reservas`
  )
  return response.data
}

async function fetchMetricas(): Promise<MetricasColoquiosData> {
  const response = await api.get<MetricasColoquiosData>(
    '/api/coloquios/metricas'
  )
  return response.data
}

export function useColoquios() {
  return useQuery({
    queryKey: coloquiosKeys.list(),
    queryFn: fetchColoquios,
  })
}

export function useCreateColoquio() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ConvocatoriaFormValues) => createColoquio(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: coloquiosKeys.all() })
    },
  })
}

export function useImportarAlumnos() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (coloquioId: string) => importarAlumnos(coloquioId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: coloquiosKeys.all() })
    },
  })
}

export function useTurnosColoquio(coloquioId: string) {
  return useQuery({
    queryKey: coloquiosKeys.turnos(coloquioId),
    queryFn: () => fetchTurnos(coloquioId),
    enabled: !!coloquioId,
  })
}

export function useMetricasColoquios() {
  return useQuery({
    queryKey: coloquiosKeys.metricas(),
    queryFn: fetchMetricas,
  })
}
