import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type {
  Calificacion,
  ImportPreview,
  ImportResult,
} from '@/features/academico/types'

export const calificacionesKeys = {
  all: ['calificaciones'] as const,
  list: (materiaId: string) => ['calificaciones', 'list', materiaId] as const,
  detail: (id: string) => ['calificaciones', 'detail', id] as const,
}

async function fetchCalificaciones(materiaId: string): Promise<Calificacion[]> {
  const response = await api.get<Calificacion[]>(
    '/api/calificaciones',
    { params: { materia_id: materiaId } }
  )
  return response.data
}

async function fetchCalificacionById(id: string): Promise<Calificacion> {
  const response = await api.get<Calificacion>(`/api/calificaciones/${id}`)
  return response.data
}

async function uploadFile(file: File, materiaId: string): Promise<ImportPreview> {
  const formData = new FormData()
  formData.append('archivo', file)
  formData.append('materia_id', materiaId)

  const response = await api.post<ImportPreview>(
    '/api/calificaciones/importar?preview=true',
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

async function confirmImport(
  materiaId: string,
  actividadIds: string[]
): Promise<ImportResult> {
  const response = await api.post<ImportResult>(
    '/api/calificaciones/importar/confirmar',
    { materia_id: materiaId, actividad_ids: actividadIds }
  )
  return response.data
}

export function useCalificaciones(materiaId: string) {
  return useQuery({
    queryKey: calificacionesKeys.list(materiaId),
    queryFn: () => fetchCalificaciones(materiaId),
    enabled: !!materiaId,
  })
}

export function useCalificacionById(id: string) {
  return useQuery({
    queryKey: calificacionesKeys.detail(id),
    queryFn: () => fetchCalificacionById(id),
    enabled: !!id,
  })
}

export function useUploadPreview() {
  return useMutation({
    mutationFn: ({ file, materiaId }: { file: File; materiaId: string }) =>
      uploadFile(file, materiaId),
  })
}

export function useConfirmImport() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      materiaId,
      actividadIds,
    }: {
      materiaId: string
      actividadIds: string[]
    }) => confirmImport(materiaId, actividadIds),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: calificacionesKeys.list(variables.materiaId),
      })
      queryClient.invalidateQueries({ queryKey: ['analisis'] })
    },
  })
}
