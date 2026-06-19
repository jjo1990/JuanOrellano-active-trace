import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { AuthGuard } from '@/shared/components/AuthGuard'

function renderWithGuard(
  initialEntries: string[],
  isAuthenticated = false
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route element={<AuthGuard />}>
              <Route path="/app" element={<div>App Content</div>} />
              <Route path="/app/perfil" element={<div>Perfil Page</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('AuthGuard', () => {
  it('redirects unauthenticated user from /app to /login', async () => {
    renderWithGuard(['/app'], false)

    expect(await screen.findByText('Login Page')).toBeInTheDocument()
  })

  it('redirects unauthenticated user from nested route to /login', async () => {
    renderWithGuard(['/app/perfil'], false)

    expect(await screen.findByText('Login Page')).toBeInTheDocument()
  })
})
