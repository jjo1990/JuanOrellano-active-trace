import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { DashboardMateria } from '@/features/academico/pages/DashboardMateria'
import { useEffect } from 'react'
import { useAuth } from '@/shared/hooks/useAuth'
import { createTestToken } from './mocks/jwt'

function LoginHelper() {
  const { login } = useAuth()

  useEffect(() => {
    const token = createTestToken({
      sub: 'user-1',
      tenant_id: 'tenant-1',
      roles: ['PROFESOR'],
    })
    login(token, 'refresh-token')
  }, [login])

  return null
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/materias/mat-1/dashboard']}>
        <AuthProvider>
          <LoginHelper />
          <Routes>
            <Route
              path="/materias/:id/dashboard"
              element={<DashboardMateria />}
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('DashboardMateria', () => {
  it('renders the dashboard title', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Dashboard de materia')).toBeInTheDocument()
    })
  })

  it('renders all tabs', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Atrasados')).toBeInTheDocument()
      expect(screen.getByText('Ranking')).toBeInTheDocument()
      expect(screen.getByText('Notas Finales')).toBeInTheDocument()
      expect(screen.getByText('TPs sin corregir')).toBeInTheDocument()
    })
  })

  it('shows atrasados tab by default', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Juan Perez')).toBeInTheDocument()
    })
  })

  it('shows summary cards when data is loaded', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Alumnos atrasados')).toBeInTheDocument()
      expect(screen.getByText('Total calificaciones')).toBeInTheDocument()
      expect(screen.getByText('Alumnos al día')).toBeInTheDocument()
    })
  })
})
