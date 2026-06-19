import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { AppShell } from '@/shared/components/AppShell'
import { useAuth } from '@/shared/hooks/useAuth'
import { useEffect } from 'react'
import { createTestToken } from './mocks/jwt'

function LoginHelper({ roles }: { roles: string[] }) {
  const { login: setLogin } = useAuth()

  useEffect(() => {
    const token = createTestToken({
      sub: 'user-1',
      tenant_id: 'tenant-1',
      roles,
    })
    setLogin(token, 'refresh-token')
  }, [setLogin, roles])

  return null
}

function renderAppShell(roles: string[] = ['PROFESOR']) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/app']}>
        <AuthProvider>
          <LoginHelper roles={roles} />
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/app" element={<div>Dashboard Content</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('AppShell', () => {
  it('renders sidebar with navigation items', async () => {
    renderAppShell()

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })
    expect(screen.getByText('Perfil')).toBeInTheDocument()
  })

  it('renders user name and email in header', async () => {
    renderAppShell()

    await waitFor(() => {
      expect(screen.getByText('María González')).toBeInTheDocument()
    })
    expect(screen.getByText('maria@test.com')).toBeInTheDocument()
  })

  it('renders logout button', async () => {
    renderAppShell()

    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: 'Cerrar sesión' })
      ).toBeInTheDocument()
    })
  })

  it('filters menu items by role', async () => {
    renderAppShell(['ALUMNO'])

    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Perfil')).toBeInTheDocument()
    })
  })
})
