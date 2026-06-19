import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Encuentro,
  EncuentroFormValues,
  InstanciaEncuentro,
  Guardia,
  GuardiaFormValues,
} from '@/features/coordinacion/types'

export const encuentrosKeys = {
  all: () => ['encuentros'] as const,
  list: (cohorteId?: string) =>
    ['encuentros', 'list', cohorteId ?? ''] as const,
  instancias: (encuentroId: string) =>
    ['encuentros', 'instancias', encuentroId] as const,
  guardias: (filters?: Record<string, string>) =>
    ['encuentros', 'guardias', filters ?? {}] as const,
}

async function fetchEncuentros(
  cohorteId?: string
): Promise<Encuentro[]> {
  const params: Record<string, string> = {}
  if (cohorteId) params.cohorte_id = cohorteId

  const response = await api.get<Encuentro[]>('/api/encuentros', { params })
  return response.data
}

async function createEncuentro(
  data: EncuentroFormValues
): Promise<Encuentro> {
  const response = await api.post<Encuentro>('/api/encuentros', data)
  return response.data
}

async function fetchInstancias(
  encuentroId: string
): Promise<InstanciaEncuentro[]> {
  const response = await api.get<InstanciaEncuentro[]>(
    `/api/encuentros/${encuentroId}/instancias`
  )
  return response.data
}

async function updateInstancia(
  id: string,
  data: {
    estado?: string
    meet_url?: string
    video_url?: string
    comentario?: string
  }
): Promise<InstanciaEncuentro> {
  const response = await api.put<InstanciaEncuentro>(
    `/api/encuentros/instancias/${id}`,
    data
  )
  return response.data
}

async function fetchGuardias(
  filters?: Record<string, string>
): Promise<Guardia[]> {
  const response = await api.get<Guardia[]>('/api/guardias', {
    params: filters,
  })
  return response.data
}

async function createGuardia(data: GuardiaFormValues): Promise<Guardia> {
  const response = await api.post<Guardia>('/api/guardias', data)
  return response.data
}

export function useEncuentros(cohorteId?: string) {
  return useQuery({
    queryKey: encuentrosKeys.list(cohorteId),
    queryFn: () => fetchEncuentros(cohorteId),
  })
}

export function useCreateEncuentro() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: EncuentroFormValues) => createEncuentro(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: encuentrosKeys.all() })
    },
  })
}

export function useInstanciasEncuentro(encuentroId: string) {
  return useQuery({
    queryKey: encuentrosKeys.instancias(encuentroId),
    queryFn: () => fetchInstancias(encuentroId),
    enabled: !!encuentroId,
  })
}

export function useUpdateInstancia() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: {
        estado?: string
        meet_url?: string
        video_url?: string
        comentario?: string
      }
    }) => updateInstancia(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: encuentrosKeys.all() })
    },
  })
}

export function useGuardias(filters?: Record<string, string>) {
  return useQuery({
    queryKey: encuentrosKeys.guardias(filters),
    queryFn: () => fetchGuardias(filters),
  })
}

export function useCreateGuardia() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: GuardiaFormValues) => createGuardia(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: encuentrosKeys.all() })
    },
  })
}
