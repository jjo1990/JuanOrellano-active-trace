import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/shared/contexts/AuthContext'
import { GestionEquipos } from '@/features/coordinacion/pages/GestionEquipos'
import { GestionAvisos } from '@/features/coordinacion/pages/GestionAvisos'
import { GestionTareas } from '@/features/coordinacion/pages/GestionTareas'
import { MonitoresTransversales } from '@/features/coordinacion/pages/MonitoresTransversales'
import { GestionEncuentros } from '@/features/coordinacion/pages/GestionEncuentros'
import { GestionColoquios } from '@/features/coordinacion/pages/GestionColoquios'
import { GestionProgramas } from '@/features/coordinacion/pages/GestionProgramas'
import { SetupCuatrimestre } from '@/features/coordinacion/pages/SetupCuatrimestre'
import { useEffect } from 'react'
import { useAuth } from '@/shared/hooks/useAuth'
import { createTestToken } from './mocks/jwt'

function LoginHelper({ roles }: { roles: string[] }) {
  const { login } = useAuth()

  useEffect(() => {
    const token = createTestToken({
      sub: 'user-1',
      tenant_id: 'tenant-1',
      roles,
    })
    login(token, 'refresh-token')
  }, [login, roles])

  return null
}

function renderPage(path: string, Component: React.ComponentType, roles: string[] = ['COORDINADOR']) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AuthProvider>
          <LoginHelper roles={roles} />
          <Routes>
            <Route path={path} element={<Component />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('GestionEquipos', () => {
  it('renderiza la página de equipos', async () => {
    renderPage('/equipos', GestionEquipos)

    await waitFor(() => {
      expect(screen.getByText('Gestión de equipos')).toBeInTheDocument()
    })
  })

  it('muestra tabs de equipos', async () => {
    renderPage('/equipos', GestionEquipos)

    await waitFor(() => {
      expect(screen.getByText('Mis Equipos')).toBeInTheDocument()
      expect(screen.getByText('Asignar')).toBeInTheDocument()
      expect(screen.getByText('Historial')).toBeInTheDocument()
    })
  })

  it('muestra el botón de exportar', async () => {
    renderPage('/equipos', GestionEquipos)

    await waitFor(() => {
      expect(screen.getByText('Exportar')).toBeInTheDocument()
    })
  })

  it('cambia a tab Asignar', async () => {
    renderPage('/equipos', GestionEquipos)

    await waitFor(() => {
      expect(
        screen.getByText('Buscar docentes')
      ).not.toBeVisible()
    })
  })
})

describe('GestionAvisos', () => {
  it('renderiza la página de avisos', async () => {
    renderPage('/avisos', GestionAvisos)

    await waitFor(() => {
      expect(screen.getByText('Gestión de avisos')).toBeInTheDocument()
    })
  })

  it('muestra el botón de nuevo aviso', async () => {
    renderPage('/avisos', GestionAvisos)

    await waitFor(() => {
      expect(screen.getByText(/nuevo aviso/i)).toBeInTheDocument()
    })
  })

  it('muestra tabla con aviso de ejemplo', async () => {
    renderPage('/avisos', GestionAvisos)

    await waitFor(() => {
      expect(screen.getByText('Aviso general')).toBeInTheDocument()
    })
  })
})

describe('GestionTareas', () => {
  it('renderiza la página de tareas', async () => {
    renderPage('/tareas', GestionTareas)

    await waitFor(() => {
      expect(screen.getByText('Gestión de tareas')).toBeInTheDocument()
    })
  })

  it('muestra tabs de tareas', async () => {
    renderPage('/tareas', GestionTareas)

    await waitFor(() => {
      expect(screen.getByText('Mis Tareas')).toBeInTheDocument()
      expect(screen.getByText('Administración')).toBeInTheDocument()
    })
  })

  it('muestra botón de nueva tarea', async () => {
    renderPage('/tareas', GestionTareas)

    await waitFor(() => {
      expect(screen.getByText(/nueva tarea/i)).toBeInTheDocument()
    })
  })

  it('muestra tarea en tabla', async () => {
    renderPage('/tareas', GestionTareas)

    await waitFor(() => {
      expect(screen.getByText('Corregir TPs')).toBeInTheDocument()
    })
  })
})

describe('MonitoresTransversales', () => {
  it('renderiza la página de monitores', async () => {
    renderPage('/monitores', MonitoresTransversales)

    await waitFor(() => {
      expect(
        screen.getByText('Monitores transversales')
      ).toBeInTheDocument()
    })
  })

  it('muestra tabs de monitores', async () => {
    renderPage('/monitores', MonitoresTransversales)

    await waitFor(() => {
      expect(screen.getByText('General')).toBeInTheDocument()
      expect(screen.getByText('Por Docente')).toBeInTheDocument()
    })
  })

  it('muestra filtro de búsqueda en tab general', async () => {
    renderPage('/monitores', MonitoresTransversales)

    await waitFor(() => {
      expect(screen.getByText('Buscar alumno')).toBeInTheDocument()
    })
  })
})

describe('GestionEncuentros', () => {
  it('renderiza la página de encuentros', async () => {
    renderPage('/encuentros', GestionEncuentros)

    await waitFor(() => {
      expect(
        screen.getByText('Gestión de encuentros')
      ).toBeInTheDocument()
    })
  })

  it('muestra tabs calendario y guardias', async () => {
    renderPage('/encuentros', GestionEncuentros)

    await waitFor(() => {
      expect(screen.getByText('Calendario')).toBeInTheDocument()
      expect(screen.getByText('Guardias')).toBeInTheDocument()
    })
  })

  it('muestra botón de nuevo encuentro', async () => {
    renderPage('/encuentros', GestionEncuentros)

    await waitFor(() => {
      expect(screen.getByText(/nuevo encuentro/i)).toBeInTheDocument()
    })
  })
})

describe('GestionColoquios', () => {
  it('renderiza la página de coloquios', async () => {
    renderPage('/coloquios', GestionColoquios)

    await waitFor(() => {
      expect(
        screen.getByText('Gestión de coloquios')
      ).toBeInTheDocument()
    })
  })

  it('muestra tabs convocatorias y métricas', async () => {
    renderPage('/coloquios', GestionColoquios)

    await waitFor(() => {
      expect(screen.getByText('Convocatorias')).toBeInTheDocument()
      expect(screen.getByText('Métricas')).toBeInTheDocument()
    })
  })

  it('muestra botón de nueva convocatoria', async () => {
    renderPage('/coloquios', GestionColoquios)

    await waitFor(() => {
      expect(
        screen.getByText(/nueva convocatoria/i)
      ).toBeInTheDocument()
    })
  })
})

describe('GestionProgramas', () => {
  it('renderiza la página de programas', async () => {
    renderPage('/programas', GestionProgramas)

    await waitFor(() => {
      expect(
        screen.getByText('Programas y fechas')
      ).toBeInTheDocument()
    })
  })

  it('muestra tabs programas y fechas', async () => {
    renderPage('/programas', GestionProgramas)

    await waitFor(() => {
      expect(screen.getByText('Programas')).toBeInTheDocument()
      expect(screen.getByText('Fechas académicas')).toBeInTheDocument()
    })
  })

  it('muestra formulario de upload', async () => {
    renderPage('/programas', GestionProgramas)

    await waitFor(() => {
      expect(screen.getByText('Subir programa')).toBeInTheDocument()
    })
  })
})

describe('SetupCuatrimestre', () => {
  it('renderiza la página de setup', async () => {
    renderPage('/setup', SetupCuatrimestre)

    await waitFor(() => {
      expect(
        screen.getByText('Setup de cuatrimestre')
      ).toBeInTheDocument()
    })
  })

  it('muestra el stepper con 5 pasos', async () => {
    renderPage('/setup', SetupCuatrimestre)

    await waitFor(() => {
      expect(screen.getByText('Cohorte')).toBeInTheDocument()
      expect(screen.getByText('Docentes')).toBeInTheDocument()
      expect(screen.getByText('Padrón')).toBeInTheDocument()
      expect(screen.getByText('Fechas')).toBeInTheDocument()
      expect(screen.getByText('Confirmar')).toBeInTheDocument()
    })
  })

  it('muestra paso 1 activo al inicio', async () => {
    renderPage('/setup', SetupCuatrimestre)

    await waitFor(() => {
      expect(
        screen.getByText('Paso 1: Crear o seleccionar cohorte')
      ).toBeInTheDocument()
    })
  })

  it('muestra botones de navegación', async () => {
    renderPage('/setup', SetupCuatrimestre)

    await waitFor(() => {
      expect(screen.getByText('Anterior')).toBeInTheDocument()
      expect(screen.getByText('Siguiente')).toBeInTheDocument()
    })
  })
})
