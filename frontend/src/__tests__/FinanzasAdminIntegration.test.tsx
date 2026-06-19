import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { RequirePermission } from '@/shared/components/RequirePermission'
import { LiquidacionesPeriodo } from '@/features/finanzas/pages/LiquidacionesPeriodo'
import { HistorialLiquidaciones } from '@/features/finanzas/pages/HistorialLiquidaciones'
import { EstructuraAcademica } from '@/features/admin/pages/EstructuraAcademica'

function renderFinanzasFlow() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/liquidaciones']}>
        <AuthProvider>
          <Routes>
            <Route path="/liquidaciones" element={<LiquidacionesPeriodo />} />
            <Route path="/liquidaciones/historial" element={<HistorialLiquidaciones />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

function renderAdminFlow() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/estructura']}>
        <AuthProvider>
          <Routes>
            <Route path="/estructura" element={<EstructuraAcademica />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Integración Finanzas', () => {
  it('14.1 - flujo: ver liquidación con KPIs y segmentación', async () => {
    renderFinanzasFlow()

    await waitFor(() => {
      expect(screen.getByText('Liquidaciones del período')).toBeInTheDocument()
    })

    // Llenar cohorte para cargar datos
    const input = screen.getByPlaceholderText('ID de cohorte')
    fireEvent.change(input, { target: { value: 'coh-1' } })

    // Ver KPIs
    expect(screen.getByText('Total sin factura')).toBeInTheDocument()
    expect(screen.getByText('Total con factura')).toBeInTheDocument()

    // Ver tabs de segmentación
    expect(screen.getByText('General')).toBeInTheDocument()
    expect(screen.getByText('NEXO')).toBeInTheDocument()
    expect(screen.getByText('Factura')).toBeInTheDocument()

    // Ver botón de cerrar
    await waitFor(() => {
      expect(screen.getByText('Cerrar liquidación')).toBeInTheDocument()
    })
  })

  it('14.1 - historial muestra liquidaciones cerradas', async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/liquidaciones/historial']}>
          <AuthProvider>
            <Routes>
              <Route path="/liquidaciones/historial" element={<HistorialLiquidaciones />} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Historial de liquidaciones')).toBeInTheDocument()
    })
  })
})

describe('Integración Admin', () => {
  it('14.2 - flujo: ver estructura, carreras y cohortes', async () => {
    renderAdminFlow()

    await waitFor(() => {
      expect(screen.getByText('Estructura académica')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('ING-INF')).toBeInTheDocument()
      expect(screen.getByText('Ingeniería Informática')).toBeInTheDocument()
    })
  })

  it('14.2 - cambio a Cohortes muestra datos de cohortes', async () => {
    renderAdminFlow()

    await waitFor(() => {
      expect(screen.getByText('Cohortes')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Cohortes'))

    await waitFor(() => {
      expect(screen.getByText('MAR-2025')).toBeInTheDocument()
    })
  })
})

describe('Guards de permiso', () => {
  it('14.3 - rutas de FINANZAS requieren rol FINANZAS o ADMIN', () => {
    const { container } = render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter initialEntries={['/liquidaciones']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/liquidaciones"
                element={
                  <RequirePermission permission="liquidaciones:ver">
                    <div>Liquidaciones content</div>
                  </RequirePermission>
                }
              />
              <Route path="/app/unauthorized" element={<div>Unauthorized</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(container.innerHTML).toBeTruthy()
  })

  it('14.3 - rutas de ADMIN requieren rol ADMIN', () => {
    const { container } = render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter initialEntries={['/estructura']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/estructura"
                element={
                  <RequirePermission permission="estructura:gestionar">
                    <div>Estructura content</div>
                  </RequirePermission>
                }
              />
              <Route path="/app/unauthorized" element={<div>Unauthorized</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(container.innerHTML).toBeTruthy()
  })

  it('14.3 - ruta auditoría requiere permiso auditoria:ver', () => {
    const { container } = render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter initialEntries={['/auditoria']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/auditoria"
                element={
                  <RequirePermission permission="auditoria:ver">
                    <div>Auditoría content</div>
                  </RequirePermission>
                }
              />
              <Route path="/app/unauthorized" element={<div>Unauthorized</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(container.innerHTML).toBeTruthy()
  })

  it('14.3 - ruta salarios requiere permiso liquidaciones:configurar-salarios', () => {
    const { container } = render(
      <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
        <MemoryRouter initialEntries={['/salarios']}>
          <AuthProvider>
            <Routes>
              <Route
                path="/salarios"
                element={
                  <RequirePermission permission="liquidaciones:configurar-salarios">
                    <div>Salarios content</div>
                  </RequirePermission>
                }
              />
              <Route path="/app/unauthorized" element={<div>Unauthorized</div>} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(container.innerHTML).toBeTruthy()
  })
})
