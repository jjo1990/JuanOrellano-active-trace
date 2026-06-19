import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type { Factura, FacturaFilters } from '@/features/finanzas/types'

export const facturasKeys = {
  all: ['facturas'] as const,
  list: (filters: FacturaFilters) => ['facturas', 'list', filters] as const,
}

async function fetchFacturas(filters: FacturaFilters): Promise<Factura[]> {
  const params: Record<string, string> = {}
  if (filters.docente) params.docente = filters.docente
  if (filters.estado) params.estado = filters.estado
  if (filters.fecha_desde) params.fecha_desde = filters.fecha_desde
  if (filters.fecha_hasta) params.fecha_hasta = filters.fecha_hasta
  if (filters.search) params.search = filters.search
  const response = await api.get<Factura[]>('/api/facturas', { params })
  return response.data
}

async function cambiarEstadoFactura(
  id: string,
  nuevoEstado: 'Pendiente' | 'Abonada'
): Promise<Factura> {
  const response = await api.put<Factura>(`/api/facturas/${id}/estado`, {
    estado: nuevoEstado,
  })
  return response.data
}

export function useFacturas(filters: FacturaFilters) {
  return useQuery({
    queryKey: facturasKeys.list(filters),
    queryFn: () => fetchFacturas(filters),
  })
}

export function useCambiarEstadoFactura() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      estado,
    }: {
      id: string
      estado: 'Pendiente' | 'Abonada'
    }) => cambiarEstadoFactura(id, estado),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: facturasKeys.all })
    },
  })
}
