import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Tarea,
  TareaFilters,
  TareaFormValues,
  ComentarioTarea,
} from '@/features/coordinacion/types'

export const tareasKeys = {
  all: () => ['tareas'] as const,
  list: (filters?: TareaFilters) => ['tareas', 'list', filters ?? {}] as const,
  detalle: (id: string) => ['tareas', 'detalle', id] as const,
  comentarios: (tareaId: string) =>
    ['tareas', 'comentarios', tareaId] as const,
}

async function fetchTareas(filters?: TareaFilters): Promise<Tarea[]> {
  const params: Record<string, string> = {}
  if (filters?.estado) params.estado = filters.estado
  if (filters?.materia_id) params.materia_id = filters.materia_id
  if (filters?.asignado_a_id) params.asignado_a_id = filters.asignado_a_id

  const response = await api.get<Tarea[]>('/api/tareas', { params })
  return response.data
}

async function createTarea(data: TareaFormValues): Promise<Tarea> {
  const response = await api.post<Tarea>('/api/tareas', data)
  return response.data
}

async function updateTarea(
  id: string,
  data: Partial<TareaFormValues>
): Promise<Tarea> {
  const response = await api.put<Tarea>(`/api/tareas/${id}`, data)
  return response.data
}

async function changeEstado(
  id: string,
  estado: string,
  comentario?: string
): Promise<Tarea> {
  const response = await api.put<Tarea>(`/api/tareas/${id}/estado`, {
    estado,
    comentario,
  })
  return response.data
}

async function delegarTarea(
  id: string,
  nuevo_asignado_id: string
): Promise<Tarea> {
  const response = await api.post<Tarea>(`/api/tareas/${id}/delegar`, {
    asignado_a_id: nuevo_asignado_id,
  })
  return response.data
}

async function fetchComentarios(
  tareaId: string
): Promise<ComentarioTarea[]> {
  const response = await api.get<ComentarioTarea[]>(
    `/api/tareas/${tareaId}/comentarios`
  )
  return response.data
}

async function addComentario(
  tareaId: string,
  texto: string
): Promise<ComentarioTarea> {
  const response = await api.post<ComentarioTarea>(
    `/api/tareas/${tareaId}/comentarios`,
    { texto }
  )
  return response.data
}

export function useTareas(filters?: TareaFilters) {
  return useQuery({
    queryKey: tareasKeys.list(filters),
    queryFn: () => fetchTareas(filters),
  })
}

export function useCreateTarea() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: TareaFormValues) => createTarea(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tareasKeys.all() })
    },
  })
}

export function useUpdateTarea() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TareaFormValues> }) =>
      updateTarea(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tareasKeys.all() })
    },
  })
}

export function useChangeEstado() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      estado,
      comentario,
    }: {
      id: string
      estado: string
      comentario?: string
    }) => changeEstado(id, estado, comentario),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tareasKeys.all() })
    },
  })
}

export function useDelegarTarea() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      id,
      nuevo_asignado_id,
    }: {
      id: string
      nuevo_asignado_id: string
    }) => delegarTarea(id, nuevo_asignado_id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: tareasKeys.all() })
    },
  })
}

export function useComentariosTarea(tareaId: string) {
  return useQuery({
    queryKey: tareasKeys.comentarios(tareaId),
    queryFn: () => fetchComentarios(tareaId),
    enabled: !!tareaId,
  })
}

export function useAddComentario() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ tareaId, texto }: { tareaId: string; texto: string }) =>
      addComentario(tareaId, texto),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: tareasKeys.comentarios(variables.tareaId),
      })
    },
  })
}
