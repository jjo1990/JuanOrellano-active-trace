import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { ComunicarAtrasados } from '@/features/academico/pages/ComunicarAtrasados'
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
      <MemoryRouter initialEntries={['/materias/mat-1/comunicar']}>
        <AuthProvider>
          <LoginHelper />
          <Routes>
            <Route
              path="/materias/:id/comunicar"
              element={<ComunicarAtrasados />}
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ComunicarAtrasados', () => {
  it('renders the page title', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Comunicar atrasados')).toBeInTheDocument()
    })
  })

  it('renders all tabs', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('Previsualizar y enviar')
      ).toBeInTheDocument()
      expect(screen.getByText('Tracking')).toBeInTheDocument()
      expect(screen.getByText('Historial')).toBeInTheDocument()
    })
  })

  it('shows destinatarioselection on the first tab', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('1. Seleccioná los destinatarios')
      ).toBeInTheDocument()
    })
  })

  it('shows preview button', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('Previsualizar mensaje')
      ).toBeInTheDocument()
    })
  })

  it('shows select all / deselect all buttons', async () => {
    renderPage()

    await waitFor(() => {
      expect(
        screen.getByText('Seleccionar todos')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Deseleccionar todos')
      ).toBeInTheDocument()
    })
  })
})
