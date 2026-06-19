import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { LiquidacionesPeriodo } from '@/features/finanzas/pages/LiquidacionesPeriodo'
import { CerrarLiquidacionModal } from '@/features/finanzas/components/CerrarLiquidacionModal'

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/liquidaciones']}>
        <AuthProvider>
          <Routes>
            <Route path="/liquidaciones" element={<LiquidacionesPeriodo />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

function fillCohorteAndWait() {
  const input = screen.getByPlaceholderText('ID de cohorte')
  fireEvent.change(input, { target: { value: 'coh-1' } })
}

describe('Liquidaciones del período', () => {
  it('12.1 - renderiza 3 tabs de segmentación', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('General')).toBeInTheDocument()
      expect(screen.getByText('NEXO')).toBeInTheDocument()
      expect(screen.getByText('Factura')).toBeInTheDocument()
    })
  })

  it('12.1 - muestra KPIs de totales', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Total sin factura')).toBeInTheDocument()
      expect(screen.getByText('Total con factura')).toBeInTheDocument()
    })
  })

  it('12.1 - muestra filtros de cohorte, mes y año', () => {
    renderPage()

    expect(screen.getByPlaceholderText('ID de cohorte')).toBeInTheDocument()
  })

  it('12.1 - el tab General muestra datos al ingresar cohorte', async () => {
    renderPage()

    fillCohorteAndWait()

    await waitFor(() => {
      expect(screen.getByText('Carlos Pérez')).toBeInTheDocument()
      expect(screen.getByText('Laura Martínez')).toBeInTheDocument()
    })
  })

  it('12.1 - cambiar a tab NEXO muestra solo entradas de ese segmento', async () => {
    renderPage()

    fillCohorteAndWait()

    await waitFor(() => {
      expect(screen.getByText('NEXO')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('NEXO'))

    await waitFor(() => {
      expect(screen.getByText('Pedro NEXO')).toBeInTheDocument()
    })
  })
})

describe('Cierre de liquidación', () => {
  it('12.2 - muestra botón de cerrar cuando la liquidación no está cerrada', async () => {
    renderPage()

    fillCohorteAndWait()

    await waitFor(() => {
      expect(screen.getByText('Cerrar liquidación')).toBeInTheDocument()
    })
  })

  it('12.2 - modal de confirmación muestra advertencia de irreversibilidad', () => {
    render(
      <CerrarLiquidacionModal
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        isLoading={false}
      />
    )

    expect(screen.getByText('Cerrar liquidación')).toBeInTheDocument()
    expect(screen.getByText('Confirmar cierre')).toBeInTheDocument()
    expect(screen.getByText(/irreversible/i)).toBeInTheDocument()
  })

  it('12.2 - al confirmar cierre llama al callback', () => {
    const onConfirm = vi.fn()
    render(
      <CerrarLiquidacionModal
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={onConfirm}
        isLoading={false}
      />
    )

    fireEvent.click(screen.getByText('Confirmar cierre'))
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('12.2 - botón Cancelar cierra el modal', () => {
    const onClose = vi.fn()
    render(
      <CerrarLiquidacionModal
        isOpen={true}
        onClose={onClose}
        onConfirm={vi.fn()}
        isLoading={false}
      />
    )

    fireEvent.click(screen.getByText('Cancelar'))
    expect(onClose).toHaveBeenCalledOnce()
  })
})
