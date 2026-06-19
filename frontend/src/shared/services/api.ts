import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from 'axios'
import { authRef } from '@/shared/contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const TENANT_ID = import.meta.env.VITE_TENANT_ID ?? 'default'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

let refreshPromise: Promise<{
  access_token: string
  refresh_token: string
}> | null = null

function getRefreshPromise(): Promise<{
  access_token: string
  refresh_token: string
}> {
  if (refreshPromise !== null) {
    return refreshPromise
  }

  const storedRefreshToken = authRef.refreshToken
  if (!storedRefreshToken) {
    return Promise.reject(new Error('No refresh token available'))
  }

  refreshPromise = api
    .post('/api/auth/refresh', {
      refresh_token: storedRefreshToken,
    })
    .then((response) => {
      const data = response.data as {
        access_token: string
        refresh_token: string
      }
      authRef.setTokens(data.access_token, data.refresh_token)
      return data
    })
    .finally(() => {
      refreshPromise = null
    })

  return refreshPromise
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers.set('X-Tenant-ID', TENANT_ID)

  const token = authRef.accessToken
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (!error.response) {
      return Promise.reject(error)
    }

    const isRefreshEndpoint =
      originalRequest.url?.includes('/api/auth/refresh')

    if (
      error.response.status === 401 &&
      !originalRequest._retry &&
      !isRefreshEndpoint
    ) {
      originalRequest._retry = true

      try {
        const { access_token } = await getRefreshPromise()
        originalRequest.headers.set('Authorization', `Bearer ${access_token}`)
        return api(originalRequest)
      } catch {
        authRef.logout()
        try {
          window.location.href = '/login'
        } catch {
          // navigation may not be available in jsdom tests
        }
        return Promise.reject(error)
      }
    }

    if (error.response.status === 403) {
      try {
        window.location.href = '/app/unauthorized'
      } catch {
        // navigation may not be available in jsdom tests
      }
    }

    return Promise.reject(error)
  }
)

export default api
