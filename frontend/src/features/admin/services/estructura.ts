import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type { Carrera, Cohorte, CarreraFormValues, CohorteFormValues } from '@/features/admin/types'

export const estructuraKeys = {
  all: ['estructura'] as const,
  carreras: ['estructura', 'carreras'] as const,
  cohortes: ['estructura', 'cohortes'] as const,
}

async function fetchCarreras(): Promise<Carrera[]> {
  const response = await api.get<Carrera[]>('/api/admin/carreras')
  return response.data
}

async function fetchCohortes(): Promise<Cohorte[]> {
  const response = await api.get<Cohorte[]>('/api/admin/cohortes')
  return response.data
}

async function createCarrera(data: CarreraFormValues): Promise<Carrera> {
  const response = await api.post<Carrera>('/api/admin/carreras', data)
  return response.data
}

async function updateCarrera(
  id: string,
  data: Partial<CarreraFormValues>
): Promise<Carrera> {
  const response = await api.put<Carrera>(`/api/admin/carreras/${id}`, data)
  return response.data
}

async function toggleCarrera(id: string, activa: boolean): Promise<Carrera> {
  const response = await api.put<Carrera>(`/api/admin/carreras/${id}/estado`, {
    activa,
  })
  return response.data
}

async function createCohorte(data: CohorteFormValues): Promise<Cohorte> {
  const response = await api.post<Cohorte>('/api/admin/cohortes', data)
  return response.data
}

async function updateCohorte(
  id: string,
  data: Partial<CohorteFormValues>
): Promise<Cohorte> {
  const response = await api.put<Cohorte>(`/api/admin/cohortes/${id}`, data)
  return response.data
}

async function toggleCohorte(id: string, activa: boolean): Promise<Cohorte> {
  const response = await api.put<Cohorte>(`/api/admin/cohortes/${id}/estado`, {
    activa,
  })
  return response.data
}

export function useCarreras() {
  return useQuery({
    queryKey: estructuraKeys.carreras,
    queryFn: fetchCarreras,
  })
}

export function useCohortes() {
  return useQuery({
    queryKey: estructuraKeys.cohortes,
    queryFn: fetchCohortes,
  })
}

export function useCreateCarrera() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createCarrera,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: estructuraKeys.carreras })
    },
  })
}

export function useUpdateCarrera() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: Partial<CarreraFormValues>
    }) => updateCarrera(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: estructuraKeys.carreras })
    },
  })
}

export function useToggleCarrera() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, activa }: { id: string; activa: boolean }) =>
      toggleCarrera(id, activa),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: estructuraKeys.carreras })
    },
  })
}

export function useCreateCohorte() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createCohorte,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: estructuraKeys.cohortes })
    },
  })
}

export function useUpdateCohorte() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: Partial<CohorteFormValues>
    }) => updateCohorte(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: estructuraKeys.cohortes })
    },
  })
}

export function useToggleCohorte() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, activa }: { id: string; activa: boolean }) =>
      toggleCohorte(id, activa),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: estructuraKeys.cohortes })
    },
  })
}
