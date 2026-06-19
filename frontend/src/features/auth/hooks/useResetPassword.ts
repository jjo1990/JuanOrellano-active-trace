import { useMutation } from '@tanstack/react-query'
import * as authService from '@/features/auth/services/authService'
import type { ResetRequest } from '@/shared/types/auth.types'

export function useResetPassword() {
  return useMutation({
    mutationFn: (data: ResetRequest) => authService.reset(data),
  })
}
