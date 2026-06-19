import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import * as authService from '@/features/auth/services/authService'
import type { Login2faRequest } from '@/shared/types/auth.types'

export function useLogin2fa() {
  const { login: setAuth } = useAuth()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: Login2faRequest) => authService.login2fa(data),
    onSuccess: (result) => {
      setAuth(result.access_token, result.refresh_token)
      navigate('/app')
    },
  })
}
