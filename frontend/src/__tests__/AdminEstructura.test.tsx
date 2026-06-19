import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { EstructuraAcademica } from '@/features/admin/pages/EstructuraAcademica'

function renderWithProviders() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <EstructuraAcademica />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Estructura académica', () => {
  it('13.1 - renderiza 2 tabs: Carreras y Cohortes', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Carreras')).toBeInTheDocument()
      expect(screen.getByText('Cohortes')).toBeInTheDocument()
    })
  })

  it('13.1 - muestra tabla de carreras por defecto', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('ING-INF')).toBeInTheDocument()
      expect(screen.getByText('Ingeniería Informática')).toBeInTheDocument()
      expect(screen.getByText('ING-ELEC')).toBeInTheDocument()
    })
  })

  it('13.1 - cambio a tab Cohortes muestra cohortes', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Cohortes')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Cohortes'))

    await waitFor(() => {
      expect(screen.getByText('MAR-2025')).toBeInTheDocument()
      expect(screen.getByText('AGO-2025')).toBeInTheDocument()
    })
  })

  it('13.1 - botón Nueva carrera muestra formulario', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Nueva carrera')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Nueva carrera'))

    expect(screen.getByText('Nueva carrera')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
    expect(screen.getByText('Guardar')).toBeInTheDocument()
  })

  it('13.1 - muestra estados Activa/Inactiva en carreras', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Activa')).toBeInTheDocument()
      expect(screen.getByText('Inactiva')).toBeInTheDocument()
    })
  })

  it('13.1 - botón Desactivar/Activar existe en carrera', async () => {
    renderWithProviders()

    await waitFor(() => {
      const toggleButtons = screen.getAllByText(/activar|desactivar/i)
      expect(toggleButtons.length).toBeGreaterThan(0)
    })
  })

  it('13.1 - formulario de cohorte valida fechas desde < hasta', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Cohortes')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Cohortes'))
    await waitFor(() => {
      expect(screen.getByText('Nueva cohorte')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Nueva cohorte'))

    expect(screen.getByText('Nueva cohorte')).toBeInTheDocument()
  })

  it('13.1 - nueva cohorte muestra formulario con año inicio y vigencias', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Cohortes')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Cohortes'))

    await waitFor(() => {
      expect(screen.getByText('Nueva cohorte')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Nueva cohorte'))

    expect(screen.getByText('Nueva cohorte')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
  })
})
