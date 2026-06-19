import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type { UsuarioTenant, UsuarioFormValues } from '@/features/admin/types'

export const usuariosKeys = {
  all: ['usuarios'] as const,
  list: (rol?: string, search?: string) => ['usuarios', 'list', { rol, search }] as const,
  detalle: (id: string) => ['usuarios', 'detalle', id] as const,
}

async function fetchUsuarios(
  rol?: string,
  search?: string
): Promise<UsuarioTenant[]> {
  const params: Record<string, string> = {}
  if (rol) params.rol = rol
  if (search) params.search = search
  const response = await api.get<UsuarioTenant[]>('/api/admin/usuarios', { params })
  return response.data
}

async function createUsuario(data: UsuarioFormValues): Promise<UsuarioTenant> {
  const response = await api.post<UsuarioTenant>('/api/admin/usuarios', data)
  return response.data
}

async function updateUsuario(
  id: string,
  data: Partial<UsuarioFormValues>
): Promise<UsuarioTenant> {
  const response = await api.put<UsuarioTenant>(`/api/admin/usuarios/${id}`, data)
  return response.data
}

async function toggleUsuario(id: string, activo: boolean): Promise<void> {
  await api.put(`/api/admin/usuarios/${id}/estado`, { activo })
}

async function revealCbu(id: string): Promise<{ cbu: string }> {
  const response = await api.post<{ cbu: string }>(
    `/api/admin/usuarios/${id}/reveal-cbu`
  )
  return response.data
}

export function useUsuarios(rol?: string, search?: string) {
  return useQuery({
    queryKey: usuariosKeys.list(rol, search),
    queryFn: () => fetchUsuarios(rol, search),
  })
}

export function useCreateUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createUsuario,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usuariosKeys.all })
    },
  })
}

export function useUpdateUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string
      data: Partial<UsuarioFormValues>
    }) => updateUsuario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usuariosKeys.all })
    },
  })
}

export function useToggleUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, activo }: { id: string; activo: boolean }) =>
      toggleUsuario(id, activo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: usuariosKeys.all })
    },
  })
}
