import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { GestionSalarios } from '@/features/finanzas/pages/GestionSalarios'

function renderWithProviders() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <GestionSalarios />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Grilla salarial', () => {
  it('12.3 - renderiza 2 tabs: Salarios Base y Plus', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Salarios Base')).toBeInTheDocument()
      expect(screen.getByText('Plus')).toBeInTheDocument()
    })
  })

  it('12.3 - muestra tabla de salarios base', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('PROFESOR')).toBeInTheDocument()
      expect(screen.getByText('TUTOR')).toBeInTheDocument()
    })
  })

  it('12.3 - cambio a tab Plus muestra tabla de plus', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Plus')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Plus'))

    await waitFor(() => {
      expect(screen.getByText('ANTIGUEDAD')).toBeInTheDocument()
      expect(screen.getByText('EXTRA')).toBeInTheDocument()
    })
  })

  it('12.3 - botón Nuevo salario base muestra formulario', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Nuevo salario base')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Nuevo salario base'))

    expect(screen.getByText('Nuevo salario base')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
    expect(screen.getByText('Guardar')).toBeInTheDocument()
  })

  it('12.3 - botón Editar en salario base muestra formulario de edición', async () => {
    renderWithProviders()

    await waitFor(() => {
      const editButtons = screen.getAllByText('Editar')
      expect(editButtons.length).toBeGreaterThan(0)
    })

    fireEvent.click(screen.getAllByText('Editar')[0])

    expect(screen.getByText('Editar salario base')).toBeInTheDocument()
  })

  it('12.3 - muestra estados activo/inactivo en salarios base', async () => {
    renderWithProviders()

    await waitFor(() => {
      const activos = screen.getAllByText('Activo')
      const inactivos = screen.getAllByText('Inactivo')
      expect(activos.length).toBeGreaterThan(0)
      expect(inactivos.length).toBeGreaterThan(0)
    })
  })

  it('12.3 - botón Desactivar existe en registros activos', async () => {
    renderWithProviders()

    await waitFor(() => {
      const deactivateButtons = screen.getAllByText('Desactivar')
      expect(deactivateButtons.length).toBeGreaterThan(0)
    })
  })

  it('12.3 - formulario de plus muestra campos al abrir', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Plus')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Plus'))

    await waitFor(() => {
      expect(screen.getByText('Nuevo plus')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Nuevo plus'))

    expect(screen.getByText('Nuevo plus')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
    expect(screen.getByText('Guardar')).toBeInTheDocument()
  })
})
