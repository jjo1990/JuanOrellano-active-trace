import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  MessagePreview,
  SendRequest,
  SendResult,
  ComunicacionLote,
  ComunicacionEnvio,
} from '@/features/academico/types'

export const comunicacionesKeys = {
  all: ['comunicaciones'] as const,
  estado: (loteId: string) => ['comunicaciones', 'estado', loteId] as const,
  historial: (materiaId: string) =>
    ['comunicaciones', 'historial', materiaId] as const,
}

async function fetchPreview(
  materiaId: string,
  destinatarios: string[]
): Promise<MessagePreview> {
  const response = await api.post<MessagePreview>(
    '/api/comunicaciones/preview',
    { materia_id: materiaId, destinatarios }
  )
  return response.data
}

async function enviar(data: SendRequest): Promise<SendResult> {
  const response = await api.post<SendResult>(
    '/api/comunicaciones/enviar',
    data
  )
  return response.data
}

async function fetchEstado(loteId: string): Promise<ComunicacionEnvio[]> {
  const response = await api.get<ComunicacionEnvio[]>(
    `/api/comunicaciones/estado/${loteId}`
  )
  return response.data
}

async function fetchHistorial(materiaId: string): Promise<ComunicacionLote[]> {
  const response = await api.get<ComunicacionLote[]>(
    '/api/comunicaciones/historial',
    { params: { materia_id: materiaId } }
  )
  return response.data
}

export function usePreview() {
  return useMutation({
    mutationFn: ({
      materiaId,
      destinatarios,
    }: {
      materiaId: string
      destinatarios: string[]
    }) => fetchPreview(materiaId, destinatarios),
  })
}

export function useEnviarComunicacion() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: SendRequest) => enviar(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: comunicacionesKeys.historial(variables.materia_id),
      })
      queryClient.invalidateQueries({ queryKey: ['comunicaciones'] })
    },
  })
}

export function useEstadoEnvio(loteId: string | null) {
  return useQuery({
    queryKey: comunicacionesKeys.estado(loteId ?? ''),
    queryFn: () => fetchEstado(loteId!),
    enabled: !!loteId,
    refetchInterval: 5000,
  })
}

export function useHistorialComunicaciones(materiaId: string) {
  return useQuery({
    queryKey: comunicacionesKeys.historial(materiaId),
    queryFn: () => fetchHistorial(materiaId),
    enabled: !!materiaId,
  })
}
