import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/shared/hooks/useAuth'
import api from '@/shared/services/api'
import type { UserInfo } from '@/shared/types/auth.types'

export function useProfile() {
  const { isAuthenticated } = useAuth()

  return useQuery<UserInfo>({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await api.get<UserInfo>('/api/perfil')
      return response.data
    },
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000,
  })
}
