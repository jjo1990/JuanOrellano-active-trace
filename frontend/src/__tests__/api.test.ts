import { describe, it, expect, afterEach, vi, beforeEach } from 'vitest'
import api from '@/shared/services/api'
import { authRef } from '@/shared/contexts/AuthContext'
import { createTestToken } from './mocks/jwt'
import { server } from './mocks/server'

beforeEach(() => {
  authRef.accessToken = null
  authRef.refreshToken = null
  authRef.setTokens = (accessToken: string, refreshToken: string) => {
    authRef.accessToken = accessToken
    authRef.refreshToken = refreshToken
  }
  authRef.logout = () => {
    authRef.accessToken = null
    authRef.refreshToken = null
  }
  authRef.login = () => {}
})

afterEach(() => {
  server.resetHandlers()
})

describe('Axios interceptor', () => {
  it('attaches X-Tenant-Id header on all requests', async () => {
    const spy = vi.fn()

    server.events.on('request:start', ({ request }) => {
      spy(request.headers.get('X-Tenant-Id'))
    })

    await api.get('/api/health')

    expect(spy).toHaveBeenCalledWith('default')
  })

  it('attaches JWT header when token exists', async () => {
    const token = createTestToken({
      sub: 'user-1',
      tenant_id: 'tenant-1',
      roles: ['PROFESOR'],
    })
    authRef.accessToken = token

    const spy = vi.fn()
    server.events.on('request:start', ({ request }) => {
      spy(request.headers.get('Authorization'))
    })

    await api.get('/api/health')

    expect(spy).toHaveBeenCalledWith(`Bearer ${token}`)
  })

  it('does NOT attach JWT header when no token', async () => {
    authRef.accessToken = null

    const spy = vi.fn()
    server.events.on('request:start', ({ request }) => {
      spy(request.headers.get('Authorization'))
    })

    await api.get('/api/health')

    const calls = spy.mock.calls.filter(([val]) => val !== null)
    expect(calls).toHaveLength(0)
  })

  it('401 triggers refresh and retries original request', async () => {
    const token = createTestToken({
      sub: 'user-1',
      tenant_id: 'tenant-1',
      roles: ['PROFESOR'],
    })
    authRef.accessToken = 'expired-token'
    authRef.refreshToken = token

    const response = await api.get('/api/perfil')

    expect(response.status).toBe(200)
    expect(response.data.nombre).toBe('María')
  })

  it('failed refresh clears session and redirects', async () => {
    authRef.accessToken = 'expired-token'
    authRef.refreshToken = 'invalid-refresh'

    const logoutSpy = vi.fn()
    authRef.logout = logoutSpy

    await expect(api.get('/api/perfil')).rejects.toBeDefined()
    expect(logoutSpy).toHaveBeenCalled()
  }, 5000)
})
