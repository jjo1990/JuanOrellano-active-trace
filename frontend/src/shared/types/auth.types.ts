export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface ChallengeResponse {
  requires_2fa: true
  challenge_token: string
}

export interface Login2faRequest {
  challenge_token: string
  totp_code: string
}

export interface RefreshRequest {
  refresh_token: string
}

export interface RefreshResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LogoutRequest {
  refresh_token: string
}

export interface ForgotRequest {
  email: string
}

export interface ResetRequest {
  token: string
  new_password: string
}

export interface MessageResponse {
  message: string
}

export interface AuthUser {
  id: string
  tenantId: string
  roles: string[]
}

export interface UserInfo {
  id: string
  tenant_id: string
  email: string
  nombre: string
  apellidos: string
  display_name: string
}

export type AuthResult = LoginResponse | ChallengeResponse

export function isChallengeResponse(
  result: AuthResult
): result is ChallengeResponse {
  return 'requires_2fa' in result && result.requires_2fa === true
}

export interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface AuthContextValue extends AuthState {
  login: (accessToken: string, refreshToken: string) => void
  logout: () => void
  setTokens: (accessToken: string, refreshToken: string) => void
}
