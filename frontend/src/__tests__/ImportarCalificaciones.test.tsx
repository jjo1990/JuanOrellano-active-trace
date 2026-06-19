import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { ImportarCalificaciones } from '@/features/academico/pages/ImportarCalificaciones'
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

  return {
    user: userEvent.setup(),
    ...render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/materias/mat-1/importar']}>
          <AuthProvider>
            <LoginHelper />
            <Routes>
              <Route
                path="/materias/:id/importar"
                element={<ImportarCalificaciones />}
              />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    ),
  }
}

describe('ImportarCalificaciones', () => {
  it('renders the wizard with step indicators', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('Importar calificaciones')
      ).toBeInTheDocument()
    })

    expect(screen.getByText('Subir')).toBeInTheDocument()
    expect(screen.getByText('Previsualizar')).toBeInTheDocument()
    expect(screen.getByText('Confirmar')).toBeInTheDocument()
  })

  it('shows file upload dropzone', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByLabelText('Seleccionar archivo de calificaciones')
      ).toBeInTheDocument()
    })
  })

  it('shows step 1 as active initially', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('Paso 1: Seleccionar archivo')
      ).toBeInTheDocument()
    })
  })
})
