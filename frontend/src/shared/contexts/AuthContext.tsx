import {
  createContext,
  useCallback,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { AuthContextValue, AuthState } from '@/shared/types/auth.types'
import { decodeJwt } from '@/shared/services/jwt-decode'

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

type AuthRef = {
  accessToken: string | null
  refreshToken: string | null
  login: (accessToken: string, refreshToken: string) => void
  logout: () => void
  setTokens: (accessToken: string, refreshToken: string) => void
}

export const authRef: AuthRef = {
  accessToken: null,
  refreshToken: null,
  login: () => {},
  logout: () => {},
  setTokens: () => {},
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    accessToken: null,
    refreshToken: null,
    user: null,
    isAuthenticated: false,
    isLoading: false,
  })

  const login = useCallback(
    (accessToken: string, refreshToken: string) => {
      const jwtPayload = decodeJwt(accessToken)
      const user = jwtPayload
        ? {
            id: jwtPayload.sub,
            tenantId: jwtPayload.tenant_id,
            roles: jwtPayload.roles ?? [],
          }
        : null

      setState({
        accessToken,
        refreshToken,
        user,
        isAuthenticated: true,
        isLoading: false,
      })
    },
    []
  )

  const logout = useCallback(() => {
    setState({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })
  }, [])

  const setTokens = useCallback(
    (accessToken: string, refreshToken: string) => {
      setState((prev) => ({
        ...prev,
        accessToken,
        refreshToken,
      }))
    },
    []
  )

  authRef.accessToken = state.accessToken
  authRef.refreshToken = state.refreshToken
  authRef.login = login
  authRef.logout = logout
  authRef.setTokens = setTokens

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      login,
      logout,
      setTokens,
    }),
    [state, login, logout, setTokens]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
