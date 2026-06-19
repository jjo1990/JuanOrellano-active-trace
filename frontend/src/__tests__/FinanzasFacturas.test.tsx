import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { GestionFacturas } from '@/features/finanzas/pages/GestionFacturas'

function renderWithProviders() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <GestionFacturas />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Gestión de facturas', () => {
  it('12.4 - renderiza tabla de facturas', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Ana Factura')).toBeInTheDocument()
      expect(screen.getByText('Juan Factura')).toBeInTheDocument()
    })
  })

  it('12.4 - muestra estados Pendiente y Abonada', async () => {
    renderWithProviders()

    await waitFor(() => {
      const pendienteEls = screen.getAllByText('Pendiente')
      const abonadaEls = screen.getAllByText('Abonada')
      expect(pendienteEls.length).toBeGreaterThan(0)
      expect(abonadaEls.length).toBeGreaterThan(0)
    })
  })

  it('12.4 - tiene filtros de búsqueda y estado', () => {
    renderWithProviders()

    expect(screen.getByText('Gestión de facturas')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Buscar...')).toBeInTheDocument()
  })

  it('12.4 - botón Detalle expande información de factura', async () => {
    renderWithProviders()

    await waitFor(() => {
      const detalleButtons = screen.getAllByText('Detalle')
      expect(detalleButtons.length).toBeGreaterThan(0)
    })

    fireEvent.click(screen.getAllByText('Detalle')[0])

    await waitFor(() => {
      expect(screen.getByText('Ocultar')).toBeInTheDocument()
    })
  })

  it('12.4 - botón Marcar abonada existe en facturas pendientes', async () => {
    renderWithProviders()

    await waitFor(() => {
      const abonarButtons = screen.getAllByText('Marcar abonada')
      expect(abonarButtons.length).toBeGreaterThan(0)
    })
  })

  it('12.4 - filtro de estado tiene opciones', () => {
    renderWithProviders()

    const estadoLabels = screen.getAllByText('Estado')
    expect(estadoLabels.length).toBeGreaterThanOrEqual(1)
    const docenteLabels = screen.getAllByText('Docente')
    expect(docenteLabels.length).toBeGreaterThanOrEqual(1)
  })
})
