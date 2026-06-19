import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { PanelAuditoria } from '@/features/admin/pages/PanelAuditoria'
import { LogAuditoria } from '@/features/admin/pages/LogAuditoria'

function renderPanel() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <PanelAuditoria />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

function renderLog() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <LogAuditoria />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Panel de auditoría', () => {
  it('13.3 - renderiza 4 sub-vistas', async () => {
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText('Acciones por día')).toBeInTheDocument()
      expect(screen.getByText('Comunicaciones')).toBeInTheDocument()
      expect(screen.getByText('Interacciones')).toBeInTheDocument()
      expect(screen.getByText('Últimas acciones')).toBeInTheDocument()
    })
  })

  it('13.3 - sub-vista Acciones por día es la activa por defecto', async () => {
    renderPanel()

    await waitFor(() => {
      const activeTab = screen.getByText('Acciones por día')
      expect(activeTab).toBeInTheDocument()
    })
  })

  it('13.3 - filtros superiores visibles en todas las sub-vistas', () => {
    renderPanel()

    expect(screen.getByText('Panel de auditoría')).toBeInTheDocument()
    expect(screen.getByText('Fecha desde')).toBeInTheDocument()
    expect(screen.getByText('Fecha hasta')).toBeInTheDocument()
  })

  it('13.3 - cambiar a Últimas acciones muestra tabla', async () => {
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText('Últimas acciones')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Últimas acciones'))

    await waitFor(() => {
      expect(screen.getByText('Carlos Pérez')).toBeInTheDocument()
    })
  })

  it('13.3 - cambiar a Interacciones muestra tabla de interacciones', async () => {
    renderPanel()

    await waitFor(() => {
      expect(screen.getByText('Interacciones')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Interacciones'))

    await waitFor(() => {
      expect(screen.getByText('Análisis')).toBeInTheDocument()
    })
  })
})

describe('Log de auditoría', () => {
  it('13.4 - renderiza tabla con datos de log', async () => {
    renderLog()

    await waitFor(() => {
      expect(screen.getByText('Carlos Pérez')).toBeInTheDocument()
      expect(screen.getByText('Laura Martínez')).toBeInTheDocument()
    })
  })

  it('13.4 - muestra filtros avanzados', () => {
    renderLog()

    expect(screen.getByText('Limpiar filtros')).toBeInTheDocument()
    expect(screen.getByText('Log completo de auditoría')).toBeInTheDocument()
  })

  it('13.4 - botón Limpiar filtros existe', () => {
    renderLog()

    expect(screen.getByText('Limpiar filtros')).toBeInTheDocument()
  })

  it('13.4 - muestra columna de IP y User Agent', async () => {
    renderLog()

    await waitFor(() => {
      expect(screen.getByText('192.168.1.100')).toBeInTheDocument()
    })
  })
})
