import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type { SalarioBase, Plus, SalarioBaseFormValues, PlusFormValues } from '@/features/finanzas/types'

export const salariosKeys = {
  all: ['salarios'] as const,
  bases: ['salarios', 'bases'] as const,
  plus: ['salarios', 'plus'] as const,
}

async function fetchSalariosBase(): Promise<SalarioBase[]> {
  const response = await api.get<SalarioBase[]>('/api/salarios/base')
  return response.data
}

async function fetchPlus(): Promise<Plus[]> {
  const response = await api.get<Plus[]>('/api/salarios/plus')
  return response.data
}

async function createSalarioBase(data: SalarioBaseFormValues): Promise<SalarioBase> {
  const response = await api.post<SalarioBase>('/api/salarios/base', data)
  return response.data
}

async function updateSalarioBase(
  id: string,
  data: Partial<SalarioBaseFormValues>
): Promise<SalarioBase> {
  const response = await api.put<SalarioBase>(`/api/salarios/base/${id}`, data)
  return response.data
}

async function deactivateSalarioBase(id: string): Promise<void> {
  await api.put(`/api/salarios/base/${id}/desactivar`)
}

async function createPlus(data: PlusFormValues): Promise<Plus> {
  const response = await api.post<Plus>('/api/salarios/plus', data)
  return response.data
}

async function updatePlus(
  id: string,
  data: Partial<PlusFormValues>
): Promise<Plus> {
  const response = await api.put<Plus>(`/api/salarios/plus/${id}`, data)
  return response.data
}

async function deactivatePlus(id: string): Promise<void> {
  await api.put(`/api/salarios/plus/${id}/desactivar`)
}

export function useSalariosBase() {
  return useQuery({
    queryKey: salariosKeys.bases,
    queryFn: fetchSalariosBase,
  })
}

export function usePlus() {
  return useQuery({
    queryKey: salariosKeys.plus,
    queryFn: fetchPlus,
  })
}

export function useCreateSalarioBase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createSalarioBase,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salariosKeys.bases })
    },
  })
}

export function useUpdateSalarioBase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<SalarioBaseFormValues> }) =>
      updateSalarioBase(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salariosKeys.bases })
    },
  })
}

export function useDeactivateSalarioBase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deactivateSalarioBase,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salariosKeys.bases })
    },
  })
}

export function useCreatePlus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createPlus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salariosKeys.plus })
    },
  })
}

export function useUpdatePlus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<PlusFormValues> }) =>
      updatePlus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salariosKeys.plus })
    },
  })
}

export function useDeactivatePlus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deactivatePlus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salariosKeys.plus })
    },
  })
}
