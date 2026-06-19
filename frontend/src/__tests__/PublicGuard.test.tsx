import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { PublicGuard } from '@/shared/components/PublicGuard'
import { useAuth } from '@/shared/hooks/useAuth'
import { useEffect } from 'react'
import { createTestToken } from './mocks/jwt'

function LoginHelper() {
  const { login: setLogin } = useAuth()

  useEffect(() => {
    const token = createTestToken({
      sub: 'user-1',
      tenant_id: 'tenant-1',
      roles: ['PROFESOR'],
    })
    setLogin(token, 'refresh-token')
  }, [setLogin])

  return null
}

function renderWithGuard(initialEntries: string[], authenticated = false) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <AuthProvider>
          {authenticated && <LoginHelper />}
          <Routes>
            <Route element={<PublicGuard />}>
              <Route path="/login" element={<div>Login Page</div>} />
              <Route
                path="/forgot-password"
                element={<div>Forgot Password</div>}
              />
            </Route>
            <Route path="/app" element={<div>Dashboard</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('PublicGuard', () => {
  it('renders login page for unauthenticated user', async () => {
    renderWithGuard(['/login'], false)

    expect(await screen.findByText('Login Page')).toBeInTheDocument()
  })

  it('redirects authenticated user from /login to /app', async () => {
    renderWithGuard(['/login'], true)

    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
  })

  it('redirects authenticated user from /forgot-password to /app', async () => {
    renderWithGuard(['/forgot-password'], true)

    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
  })
})
