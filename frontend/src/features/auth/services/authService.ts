import api from '@/shared/services/api'
import type {
  LoginRequest,
  Login2faRequest,
  ForgotRequest,
  ResetRequest,
  AuthResult,
  LoginResponse,
  MessageResponse,
} from '@/shared/types/auth.types'

export async function login(data: LoginRequest): Promise<AuthResult> {
  const response = await api.post<AuthResult>('/api/auth/login', data)
  return response.data
}

export async function login2fa(data: Login2faRequest): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/api/auth/login/2fa', data)
  return response.data
}

export async function refresh(): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>('/api/auth/refresh')
  return response.data
}

export async function logout(refreshToken: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>('/api/auth/logout', {
    refresh_token: refreshToken,
  })
  return response.data
}

export async function forgot(
  data: ForgotRequest
): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>(
    '/api/auth/forgot',
    data
  )
  return response.data
}

export async function reset(data: ResetRequest): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>('/api/auth/reset', data)
  return response.data
}
