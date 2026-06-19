import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { GestionUsuarios } from '@/features/admin/pages/GestionUsuarios'

function renderWithProviders() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <GestionUsuarios />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Gestión de usuarios', () => {
  it('13.2 - renderiza tabla de usuarios', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Carlos Pérez')).toBeInTheDocument()
      expect(screen.getByText('Laura Martínez')).toBeInTheDocument()
    })
  })

  it('13.2 - muestra filtros de búsqueda', () => {
    renderWithProviders()

    expect(screen.getByText('Gestión de usuarios')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Buscar por nombre o email...')).toBeInTheDocument()
  })

  it('13.2 - muestra roles como badges', async () => {
    renderWithProviders()

    await waitFor(() => {
      const profesorBadges = screen.getAllByText('PROFESOR')
      const tutorBadges = screen.getAllByText('TUTOR')
      expect(profesorBadges.length).toBeGreaterThan(0)
      expect(tutorBadges.length).toBeGreaterThan(0)
    })
  })

  it('13.2 - muestra estados activo/inactivo', async () => {
    renderWithProviders()

    await waitFor(() => {
      const activos = screen.getAllByText('Activo')
      expect(activos.length).toBeGreaterThan(0)
    })
  })

  it('13.2 - CBU aparece enmascarado con botón Revelar', async () => {
    renderWithProviders()

    await waitFor(() => {
      const revealButtons = screen.getAllByText('Revelar')
      expect(revealButtons.length).toBeGreaterThan(0)
    })
  })

  it('13.2 - botón Nuevo usuario abre formulario', async () => {
    renderWithProviders()

    await waitFor(() => {
      expect(screen.getByText('Nuevo usuario')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Nuevo usuario'))

    expect(screen.getByText('Nuevo usuario')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
  })

  it('13.2 - botón Activar/Desactivar existe', async () => {
    renderWithProviders()

    await waitFor(() => {
      const toggleButtons = screen.getAllByText(/activar|desactivar/i)
      expect(toggleButtons.length).toBeGreaterThan(0)
    })
  })

  it('13.2 - al hacer clic en Revelar muestra CBU y cambia a Ocultar', async () => {
    renderWithProviders()

    await waitFor(() => {
      const revealButtons = screen.getAllByText('Revelar')
      expect(revealButtons.length).toBeGreaterThan(0)
    })

    fireEvent.click(screen.getAllByText('Revelar')[0])

    await waitFor(() => {
      expect(screen.getByText('Ocultar')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Ocultar'))

    await waitFor(() => {
      expect(screen.getAllByText('Revelar').length).toBe(1)
    })
  })
})
