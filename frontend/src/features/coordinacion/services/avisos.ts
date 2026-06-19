import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Aviso,
  AvisoAcknowledgment,
  AvisoFormValues,
} from '@/features/coordinacion/types'

export const avisosKeys = {
  all: () => ['avisos'] as const,
  list: (filters?: Record<string, string>) =>
    ['avisos', 'list', filters ?? {}] as const,
  acknowledgments: (avisoId: string) =>
    ['avisos', 'acknowledgments', avisoId] as const,
}

async function fetchAvisos(
  filters?: Record<string, string>
): Promise<Aviso[]> {
  const response = await api.get<Aviso[]>('/api/avisos', {
    params: filters,
  })
  return response.data
}

async function createAviso(data: AvisoFormValues): Promise<Aviso> {
  const response = await api.post<Aviso>('/api/avisos', data)
  return response.data
}

async function updateAviso(
  id: string,
  data: AvisoFormValues
): Promise<Aviso> {
  const response = await api.put<Aviso>(`/api/avisos/${id}`, data)
  return response.data
}

async function deleteAviso(id: string): Promise<void> {
  await api.delete(`/api/avisos/${id}`)
}

async function fetchAcknowledgments(
  avisoId: string
): Promise<AvisoAcknowledgment[]> {
  const response = await api.get<AvisoAcknowledgment[]>(
    `/api/avisos/${avisoId}/acknowledgments`
  )
  return response.data
}

export function useAvisos(filters?: Record<string, string>) {
  return useQuery({
    queryKey: avisosKeys.list(filters),
    queryFn: () => fetchAvisos(filters),
  })
}

export function useCreateAviso() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: AvisoFormValues) => createAviso(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: avisosKeys.all() })
    },
  })
}

export function useUpdateAviso() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AvisoFormValues }) =>
      updateAviso(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: avisosKeys.all() })
    },
  })
}

export function useDeleteAviso() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => deleteAviso(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: avisosKeys.all() })
    },
  })
}

export function useAvisoAcknowledgments(avisoId: string) {
  return useQuery({
    queryKey: avisosKeys.acknowledgments(avisoId),
    queryFn: () => fetchAcknowledgments(avisoId),
    enabled: !!avisoId,
  })
}
