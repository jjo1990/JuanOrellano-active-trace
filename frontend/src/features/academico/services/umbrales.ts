import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type { Umbral } from '@/features/academico/types'

export const umbralesKeys = {
  all: ['umbrales'] as const,
  byMateria: (materiaId: string) => ['umbrales', materiaId] as const,
}

async function fetchUmbral(materiaId: string): Promise<Umbral> {
  const response = await api.get<Umbral>(`/api/umbrales/${materiaId}`)
  return response.data
}

async function updateUmbral(
  materiaId: string,
  porcentaje: number
): Promise<Umbral> {
  const response = await api.put<Umbral>(`/api/umbrales/${materiaId}`, {
    porcentaje,
  })
  return response.data
}

export function useUmbral(materiaId: string) {
  return useQuery({
    queryKey: umbralesKeys.byMateria(materiaId),
    queryFn: () => fetchUmbral(materiaId),
    enabled: !!materiaId,
  })
}

export function useUpdateUmbral() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      materiaId,
      porcentaje,
    }: {
      materiaId: string
      porcentaje: number
    }) => updateUmbral(materiaId, porcentaje),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: umbralesKeys.byMateria(variables.materiaId),
      })
      queryClient.invalidateQueries({ queryKey: ['analisis'] })
    },
  })
}
