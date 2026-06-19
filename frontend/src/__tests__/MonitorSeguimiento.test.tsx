import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { MonitorSeguimiento } from '@/features/academico/pages/MonitorSeguimiento'
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
      <MemoryRouter initialEntries={['/monitor']}>
        <AuthProvider>
          <LoginHelper />
          <Routes>
            <Route path="/monitor" element={<MonitorSeguimiento />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('MonitorSeguimiento', () => {
  it('renders the page title', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('Monitor de seguimiento')
      ).toBeInTheDocument()
    })
  })

  it('renders filter inputs', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByLabelText('Buscar alumno')).toBeInTheDocument()
      expect(screen.getByLabelText('Materia')).toBeInTheDocument()
      expect(screen.getByLabelText('Comisión')).toBeInTheDocument()
    })
  })

  it('renders filter and clear buttons', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Filtrar')).toBeInTheDocument()
      expect(screen.getByText('Limpiar')).toBeInTheDocument()
    })
  })

  it('shows export button when data is loaded', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Exportar')).toBeInTheDocument()
    })
  })

  it('shows monitor data in table', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Juan Perez')).toBeInTheDocument()
      expect(screen.getByText('Ana Lopez')).toBeInTheDocument()
    })
  })
})
