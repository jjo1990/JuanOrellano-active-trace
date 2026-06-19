import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Programa,
  FechaAcademica,
  FechaAcademicaFormValues,
} from '@/features/coordinacion/types'

export const programasKeys = {
  all: () => ['programas'] as const,
  list: (cohorteId?: string) =>
    ['programas', 'list', cohorteId ?? ''] as const,
  fechas: (cohorteId?: string) =>
    ['programas', 'fechas', cohorteId ?? ''] as const,
}

async function uploadPrograma(data: FormData): Promise<Programa> {
  const response = await api.post<Programa>('/api/programas', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

async function fetchProgramas(cohorteId?: string): Promise<Programa[]> {
  const params: Record<string, string> = {}
  if (cohorteId) params.cohorte_id = cohorteId

  const response = await api.get<Programa[]>('/api/programas', { params })
  return response.data
}

async function fetchFechasAcademicas(
  cohorteId?: string
): Promise<FechaAcademica[]> {
  const params: Record<string, string> = {}
  if (cohorteId) params.cohorte_id = cohorteId

  const response = await api.get<FechaAcademica[]>(
    '/api/fechas-academicas',
    { params }
  )
  return response.data
}

async function createFechaAcademica(
  data: FechaAcademicaFormValues
): Promise<FechaAcademica> {
  const response = await api.post<FechaAcademica>(
    '/api/fechas-academicas',
    data
  )
  return response.data
}

async function updateFechaAcademica(
  id: string,
  data: FechaAcademicaFormValues
): Promise<FechaAcademica> {
  const response = await api.put<FechaAcademica>(
    `/api/fechas-academicas/${id}`,
    data
  )
  return response.data
}

async function deleteFechaAcademica(id: string): Promise<void> {
  await api.delete(`/api/fechas-academicas/${id}`)
}

export function useUploadPrograma() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: FormData) => uploadPrograma(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: programasKeys.all() })
    },
  })
}

export function useProgramas(cohorteId?: string) {
  return useQuery({
    queryKey: programasKeys.list(cohorteId),
    queryFn: () => fetchProgramas(cohorteId),
  })
}

export function useFechasAcademicas(cohorteId?: string) {
  return useQuery({
    queryKey: programasKeys.fechas(cohorteId),
    queryFn: () => fetchFechasAcademicas(cohorteId),
  })
}

export function useCreateFechaAcademica() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: FechaAcademicaFormValues) =>
      createFechaAcademica(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: programasKeys.all() })
    },
  })
}

export function useUpdateFechaAcademica() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: FechaAcademicaFormValues
    }) => updateFechaAcademica(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: programasKeys.all() })
    },
  })
}

export function useDeleteFechaAcademica() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => deleteFechaAcademica(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: programasKeys.all() })
    },
  })
}
