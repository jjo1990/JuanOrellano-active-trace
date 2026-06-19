import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  LiquidacionPeriodo,
  LiquidacionCerrada,
} from '@/features/finanzas/types'

export const liquidacionesKeys = {
  all: ['liquidaciones'] as const,
  periodo: (cohorteId: string, mes: number, anio: number) =>
    ['liquidaciones', 'periodo', cohorteId, mes, anio] as const,
  historial: (cohorteId?: string, mes?: number, anio?: number) =>
    ['liquidaciones', 'historial', { cohorteId, mes, anio }] as const,
  detalle: (id: string) => ['liquidaciones', 'detalle', id] as const,
}

async function fetchLiquidacionPeriodo(
  cohorteId: string,
  mes: number,
  anio: number
): Promise<LiquidacionPeriodo> {
  const response = await api.get<LiquidacionPeriodo>('/api/liquidaciones/periodo', {
    params: { cohorte_id: cohorteId, mes, anio },
  })
  return response.data
}

async function fetchHistorial(
  cohorteId?: string,
  mes?: number,
  anio?: number
): Promise<LiquidacionCerrada[]> {
  const params: Record<string, string | number> = {}
  if (cohorteId) params.cohorte_id = cohorteId
  if (mes) params.mes = mes
  if (anio) params.anio = anio
  const response = await api.get<LiquidacionCerrada[]>('/api/liquidaciones/historial', {
    params,
  })
  return response.data
}

async function fetchDetalle(id: string): Promise<LiquidacionPeriodo> {
  const response = await api.get<LiquidacionPeriodo>(`/api/liquidaciones/${id}`)
  return response.data
}

async function cerrarLiquidacion(
  cohorteId: string,
  mes: number,
  anio: number
): Promise<void> {
  await api.post('/api/liquidaciones/cerrar', {
    cohorte_id: cohorteId,
    mes,
    anio,
  })
}

export function useLiquidacionPeriodo(
  cohorteId: string,
  mes: number,
  anio: number
) {
  return useQuery({
    queryKey: liquidacionesKeys.periodo(cohorteId, mes, anio),
    queryFn: () => fetchLiquidacionPeriodo(cohorteId, mes, anio),
    enabled: !!cohorteId && !!mes && !!anio,
  })
}

export function useHistorial(
  cohorteId?: string,
  mes?: number,
  anio?: number
) {
  return useQuery({
    queryKey: liquidacionesKeys.historial(cohorteId, mes, anio),
    queryFn: () => fetchHistorial(cohorteId, mes, anio),
  })
}

export function useDetalleLiquidacion(id: string) {
  return useQuery({
    queryKey: liquidacionesKeys.detalle(id),
    queryFn: () => fetchDetalle(id),
    enabled: !!id,
  })
}

export function useCerrarLiquidacion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      cohorteId,
      mes,
      anio,
    }: {
      cohorteId: string
      mes: number
      anio: number
    }) => cerrarLiquidacion(cohorteId, mes, anio),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: liquidacionesKeys.all })
    },
  })
}
