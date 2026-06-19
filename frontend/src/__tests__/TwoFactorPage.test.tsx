import { describe, it, expect } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { TwoFactorPage } from '@/features/auth/pages/TwoFactorPage'

function renderWithRoutes() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter
        initialEntries={[
          { pathname: '/2fa', state: { challenge_token: 'challenge-token-123' } },
        ]}
      >
        <AuthProvider>
          <Routes>
            <Route path="/2fa" element={<TwoFactorPage />} />
            <Route path="/app" element={<div>Dashboard Content</div>} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('TwoFactorPage', () => {
  it('renders TOTP input and submit button', () => {
    renderWithRoutes()

    expect(
      screen.getByLabelText('Código de autenticación (6 dígitos)')
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Verificar' })
    ).toBeInTheDocument()
  })

  it('valid 2FA code navigates to /app', async () => {
    renderWithRoutes()

    fireEvent.change(
      screen.getByLabelText('Código de autenticación (6 dígitos)'),
      { target: { value: '123456' } }
    )
    fireEvent.click(screen.getByRole('button', { name: 'Verificar' }))

    await waitFor(() => {
      expect(screen.getByText('Dashboard Content')).toBeInTheDocument()
    })
  })

  it('invalid 2FA code shows error', async () => {
    renderWithRoutes()

    fireEvent.change(
      screen.getByLabelText('Código de autenticación (6 dígitos)'),
      { target: { value: '000000' } }
    )
    fireEvent.click(screen.getByRole('button', { name: 'Verificar' }))

    await waitFor(() => {
      const errorBox = document.querySelector('.bg-red-50')
      expect(errorBox).toBeInTheDocument()
    })
  })
})
