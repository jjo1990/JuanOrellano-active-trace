import { useState, useCallback } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { ConvocatoriaForm } from '@/features/coordinacion/components/ConvocatoriaForm'
import { ReservasTurno } from '@/features/coordinacion/components/ReservasTurno'
import { MetricasColoquios } from '@/features/coordinacion/components/MetricasColoquios'
import {
  useColoquios,
  useCreateColoquio,
  useImportarAlumnos,
} from '@/features/coordinacion/services/coloquios'
import type {
  Coloquio,
  ConvocatoriaFormValues,
} from '@/features/coordinacion/types'

type Tab = 'convocatorias' | 'metricas'

const tabs: { key: Tab; label: string }[] = [
  { key: 'convocatorias', label: 'Convocatorias' },
  { key: 'metricas', label: 'Métricas' },
]

export function GestionColoquios() {
  const [activeTab, setActiveTab] = useState<Tab>('convocatorias')
  const [showForm, setShowForm] = useState(false)
  const [selectedColoquio, setSelectedColoquio] = useState<string | null>(null)
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data, isLoading } = useColoquios()
  const createMutation = useCreateColoquio()
  const importarMutation = useImportarAlumnos()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleCreate = useCallback(
    (formData: ConvocatoriaFormValues) => {
      createMutation.mutate(formData, {
        onSuccess: () => {
          showMessage('Convocatoria creada.', 'success')
          setShowForm(false)
        },
        onError: () =>
          showMessage('Error al crear convocatoria.', 'error'),
      })
    },
    [createMutation, showMessage]
  )

  const handleImportar = useCallback(
    (coloquioId: string) => {
      importarMutation.mutate(coloquioId, {
        onSuccess: (result) => {
          showMessage(
            `${result.alumnos_importados} alumnos importados.`,
            'success'
          )
        },
        onError: () =>
          showMessage('Error al importar alumnos.', 'error'),
      })
    },
    [importarMutation, showMessage]
  )

  const columns: Column<Coloquio>[] = [
    {
      key: 'materia',
      header: 'Materia',
      sortable: true,
      accessor: (row) => row.materia_nombre ?? row.materia_id,
    },
    {
      key: 'cohorte',
      header: 'Cohorte',
      sortable: true,
      accessor: (row) => row.cohorte_nombre ?? row.cohorte_id,
    },
    {
      key: 'dias',
      header: 'Días',
      sortable: false,
      accessor: (row) => (
        <span className="text-xs text-gray-500">{row.dias.join(', ')}</span>
      ),
    },
    {
      key: 'cupo',
      header: 'Cupo/turno',
      sortable: true,
      accessor: (row) => row.cupo_por_turno,
    },
    {
      key: 'activo',
      header: 'Estado',
      sortable: true,
      accessor: (row) => (
        <StatusBadge estado={row.activo ? 'Al día' : 'Cancelado'} />
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      sortable: false,
      className: 'text-right',
      accessor: (row) => (
        <div className="flex gap-2 justify-end">
          <button
            type="button"
            onClick={() =>
              setSelectedColoquio(
                selectedColoquio === row.id ? null : row.id
              )
            }
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            {selectedColoquio === row.id
              ? 'Ocultar turnos'
              : 'Ver turnos'}
          </button>
          <button
            type="button"
            onClick={() => handleImportar(row.id)}
            disabled={importarMutation.isPending}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            Importar alumnos
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestión de coloquios
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Convocatorias, turnos y métricas
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            + Nueva convocatoria
          </button>
        </div>
      </div>

      {message && (
        <div
          className={`mb-4 rounded-md px-4 py-3 text-sm ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      {showForm && (
        <div className="mb-6">
          <ConvocatoriaForm
            onSubmit={handleCreate}
            isLoading={createMutation.isPending}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-4 px-4" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4">
          {activeTab === 'convocatorias' && (
            <div className="space-y-4">
              <DataTable
                columns={columns}
                data={data ?? []}
                isLoading={isLoading}
                emptyMessage="No hay convocatorias creadas."
                getRowKey={(row) => row.id}
              />
              {selectedColoquio && (
                <div className="rounded-lg border border-indigo-100 bg-indigo-50/50 p-4">
                  <h4 className="text-sm font-medium text-indigo-900">
                    Reservas por turno
                  </h4>
                  <div className="mt-3">
                    <ReservasTurno coloquioId={selectedColoquio} />
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'metricas' && <MetricasColoquios />}
        </div>
      </div>
    </div>
  )
}
