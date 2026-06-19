import { useMutation } from '@tanstack/react-query'
import * as authService from '@/features/auth/services/authService'
import type { ForgotRequest } from '@/shared/types/auth.types'

export function useForgotPassword() {
  return useMutation({
    mutationFn: (data: ForgotRequest) => authService.forgot(data),
  })
}
