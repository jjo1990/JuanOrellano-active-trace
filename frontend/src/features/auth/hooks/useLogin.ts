import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import * as authService from '@/features/auth/services/authService'
import {
  isChallengeResponse,
  type LoginRequest,
} from '@/shared/types/auth.types'

export function useLogin() {
  const { login: setAuth } = useAuth()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),
    onSuccess: (result) => {
      if (isChallengeResponse(result)) {
        navigate('/2fa', { state: { challenge_token: result.challenge_token } })
      } else {
        setAuth(result.access_token, result.refresh_token)
        navigate('/app')
      }
    },
  })
}
