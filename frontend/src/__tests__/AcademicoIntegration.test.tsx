import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { ImportarCalificaciones } from '@/features/academico/pages/ImportarCalificaciones'
import { DashboardMateria } from '@/features/academico/pages/DashboardMateria'
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

function renderRoutes(paths: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={paths}>
        <AuthProvider>
          <LoginHelper />
          <Routes>
            <Route
              path="/materias/:id/importar"
              element={<ImportarCalificaciones />}
            />
            <Route
              path="/materias/:id/dashboard"
              element={<DashboardMateria />}
            />
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

describe('Academico Integration', () => {
  it('renderizar importar calificaciones correctly', async () => {
    renderRoutes(['/materias/mat-1/importar'])

    await waitFor(() => {
      expect(
        screen.getByText('Importar calificaciones')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Paso 1: Seleccionar archivo')
      ).toBeInTheDocument()
    })
  })

  it('renderizar dashboard correctly', async () => {
    renderRoutes(['/materias/mat-1/dashboard'])

    await waitFor(() => {
      expect(screen.getByText('Dashboard de materia')).toBeInTheDocument()
      expect(screen.getByText('Atrasados')).toBeInTheDocument()
      expect(screen.getByText('Ranking')).toBeInTheDocument()
    })
  })

  it('renderizar comunicar atrasados correctly', async () => {
    renderRoutes(['/materias/mat-1/comunicar'])

    await waitFor(() => {
      expect(screen.getByText('Comunicar atrasados')).toBeInTheDocument()
      expect(
        screen.getByText('Previsualizar y enviar')
      ).toBeInTheDocument()
    })
  })
})
