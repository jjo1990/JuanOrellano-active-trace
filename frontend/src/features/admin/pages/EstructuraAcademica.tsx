import { useState } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { CarreraForm } from '@/features/admin/components/CarreraForm'
import { CohorteForm } from '@/features/admin/components/CohorteForm'
import {
  useCarreras,
  useCreateCarrera,
  useUpdateCarrera,
  useToggleCarrera,
  useCohortes,
  useCreateCohorte,
  useUpdateCohorte,
  useToggleCohorte,
} from '@/features/admin/services/estructura'
import type {
  Carrera,
  CarreraFormValues,
  Cohorte,
  CohorteFormValues,
} from '@/features/admin/types'

type Tab = 'carreras' | 'cohortes'

export function EstructuraAcademica() {
  const [tab, setTab] = useState<Tab>('carreras')
  const [showCarreraForm, setShowCarreraForm] = useState(false)
  const [editingCarrera, setEditingCarrera] = useState<Carrera | null>(null)
  const [showCohorteForm, setShowCohorteForm] = useState(false)
  const [editingCohorte, setEditingCohorte] = useState<Cohorte | null>(null)

  const { data: carreras, isLoading: carrerasLoading } = useCarreras()
  const { data: cohortes, isLoading: cohortesLoading } = useCohortes()
  const createCarrera = useCreateCarrera()
  const updateCarrera = useUpdateCarrera()
  const toggleCarrera = useToggleCarrera()
  const createCohorte = useCreateCohorte()
  const updateCohorte = useUpdateCohorte()
  const toggleCohorte = useToggleCohorte()

  const carreraColumns: Column<Carrera>[] = [
    {
      key: 'codigo',
      header: 'Código',
      sortable: true,
      accessor: (row) => row.codigo,
    },
    {
      key: 'nombre',
      header: 'Nombre',
      sortable: true,
      accessor: (row) => row.nombre,
    },
    {
      key: 'estado',
      header: 'Estado',
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.activa
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          {row.activa ? 'Activa' : 'Inactiva'}
        </span>
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      accessor: (row) => (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              setEditingCarrera(row)
              setShowCarreraForm(true)
            }}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => toggleCarrera.mutate({ id: row.id, activa: !row.activa })}
            className={`text-xs ${
              row.activa
                ? 'text-red-600 hover:text-red-800'
                : 'text-green-600 hover:text-green-800'
            }`}
          >
            {row.activa ? 'Desactivar' : 'Activar'}
          </button>
        </div>
      ),
    },
  ]

  const cohorteColumns: Column<Cohorte>[] = [
    {
      key: 'nombre',
      header: 'Nombre',
      sortable: true,
      accessor: (row) => row.nombre,
    },
    {
      key: 'anio_inicio',
      header: 'Año inicio',
      sortable: true,
      accessor: (row) => row.anio_inicio,
    },
    {
      key: 'vigencia_desde',
      header: 'Vigencia desde',
      sortable: true,
      accessor: (row) =>
        new Date(row.vigencia_desde).toLocaleDateString('es-AR'),
    },
    {
      key: 'vigencia_hasta',
      header: 'Vigencia hasta',
      accessor: (row) =>
        row.vigencia_hasta
          ? new Date(row.vigencia_hasta).toLocaleDateString('es-AR')
          : '—',
    },
    {
      key: 'estado',
      header: 'Estado',
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.activa
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          {row.activa ? 'Activa' : 'Inactiva'}
        </span>
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      accessor: (row) => (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              setEditingCohorte(row)
              setShowCohorteForm(true)
            }}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => toggleCohorte.mutate({ id: row.id, activa: !row.activa })}
            className={`text-xs ${
              row.activa
                ? 'text-red-600 hover:text-red-800'
                : 'text-green-600 hover:text-green-800'
            }`}
          >
            {row.activa ? 'Cerrar' : 'Activar'}
          </button>
        </div>
      ),
    },
  ]

  const handleCarreraSubmit = (data: CarreraFormValues) => {
    if (editingCarrera) {
      updateCarrera.mutate(
        { id: editingCarrera.id, data },
        { onSuccess: () => { setShowCarreraForm(false); setEditingCarrera(null) } }
      )
    } else {
      createCarrera.mutate(data, {
        onSuccess: () => setShowCarreraForm(false),
      })
    }
  }

  const handleCohorteSubmit = (data: CohorteFormValues) => {
    if (editingCohorte) {
      updateCohorte.mutate(
        { id: editingCohorte.id, data },
        { onSuccess: () => { setShowCohorteForm(false); setEditingCohorte(null) } }
      )
    } else {
      createCohorte.mutate(data, {
        onSuccess: () => setShowCohorteForm(false),
      })
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Estructura académica
      </h1>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-4">
          <button
            type="button"
            onClick={() => setTab('carreras')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === 'carreras'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Carreras
          </button>
          <button
            type="button"
            onClick={() => setTab('cohortes')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === 'cohortes'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Cohortes
          </button>
        </nav>
      </div>

      {tab === 'carreras' && (
        <div className="space-y-4">
          {!showCarreraForm && (
            <button
              type="button"
              onClick={() => {
                setEditingCarrera(null)
                setShowCarreraForm(true)
              }}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Nueva carrera
            </button>
          )}
          {showCarreraForm && (
            <CarreraForm
              initialValues={editingCarrera ?? undefined}
              onSubmit={handleCarreraSubmit}
              onCancel={() => {
                setShowCarreraForm(false)
                setEditingCarrera(null)
              }}
              isLoading={createCarrera.isPending || updateCarrera.isPending}
            />
          )}
          <DataTable
            columns={carreraColumns}
            data={carreras ?? []}
            isLoading={carrerasLoading}
            getRowKey={(row) => row.id}
            emptyMessage="No hay carreras registradas."
          />
        </div>
      )}

      {tab === 'cohortes' && (
        <div className="space-y-4">
          {!showCohorteForm && (
            <button
              type="button"
              onClick={() => {
                setEditingCohorte(null)
                setShowCohorteForm(true)
              }}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Nueva cohorte
            </button>
          )}
          {showCohorteForm && (
            <CohorteForm
              initialValues={editingCohorte ?? undefined}
              onSubmit={handleCohorteSubmit}
              onCancel={() => {
                setShowCohorteForm(false)
                setEditingCohorte(null)
              }}
              isLoading={createCohorte.isPending || updateCohorte.isPending}
            />
          )}
          <DataTable
            columns={cohorteColumns}
            data={cohortes ?? []}
            isLoading={cohortesLoading}
            getRowKey={(row) => row.id}
            emptyMessage="No hay cohortes registradas."
          />
        </div>
      )}
    </div>
  )
}
