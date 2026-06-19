import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import * as authService from '@/features/auth/services/authService'

export function useLogout() {
  const { logout: clearAuth, refreshToken } = useAuth()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: () => {
      if (refreshToken) {
        return authService.logout(refreshToken)
      }
      return Promise.resolve({ message: 'Logged out' })
    },
    onSettled: () => {
      clearAuth()
      navigate('/login')
    },
  })
}
