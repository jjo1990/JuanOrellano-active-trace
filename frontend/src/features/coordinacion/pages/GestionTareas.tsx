import { useState, useCallback } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { TareaForm } from '@/features/coordinacion/components/TareaForm'
import { TareaWorkflow } from '@/features/coordinacion/components/TareaWorkflow'
import {
  useTareas,
  useCreateTarea,
  useChangeEstado,
  useDelegarTarea,
} from '@/features/coordinacion/services/tareas'
import type {
  Tarea,
  TareaFilters,
  TareaFormValues,
  TareaEstado,
} from '@/features/coordinacion/types'

type Tab = 'mis-tareas' | 'administracion'

const tabs: { key: Tab; label: string }[] = [
  { key: 'mis-tareas', label: 'Mis Tareas' },
  { key: 'administracion', label: 'Administración' },
]

export function GestionTareas() {
  const [activeTab, setActiveTab] = useState<Tab>('mis-tareas')
  const [showForm, setShowForm] = useState(false)
  const [filters, setFilters] = useState<TareaFilters>({})
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data, isLoading } = useTareas(filters)
  const createMutation = useCreateTarea()
  const changeEstadoMutation = useChangeEstado()
  const delegarMutation = useDelegarTarea()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleCreate = useCallback(
    (formData: TareaFormValues) => {
      createMutation.mutate(formData, {
        onSuccess: () => {
          showMessage('Tarea creada.', 'success')
          setShowForm(false)
        },
        onError: () => showMessage('Error al crear tarea.', 'error'),
      })
    },
    [createMutation, showMessage]
  )

  const handleChangeEstado = useCallback(
    (tareaId: string, estado: TareaEstado, comentario?: string) => {
      changeEstadoMutation.mutate(
        { id: tareaId, estado, comentario },
        {
          onSuccess: () =>
            showMessage(`Tarea → ${estado}`, 'success'),
          onError: () =>
            showMessage('Error al cambiar estado.', 'error'),
        }
      )
    },
    [changeEstadoMutation, showMessage]
  )

  const handleDelegar = useCallback(
    (tareaId: string, nuevoAsignadoId: string) => {
      delegarMutation.mutate(
        { id: tareaId, nuevo_asignado_id: nuevoAsignadoId },
        {
          onSuccess: () => showMessage('Tarea delegada.', 'success'),
          onError: () => showMessage('Error al delegar.', 'error'),
        }
      )
    },
    [delegarMutation, showMessage]
  )

  const columns: Column<Tarea>[] = [
    {
      key: 'titulo',
      header: 'Título',
      sortable: true,
      accessor: (row) => row.titulo,
    },
    {
      key: 'asignado_por',
      header: 'Asignado por',
      sortable: true,
      accessor: (row) => row.asignado_por_nombre,
    },
    {
      key: 'asignado_a',
      header: 'Asignado a',
      sortable: true,
      accessor: (row) => row.asignado_a_nombre,
    },
    {
      key: 'estado',
      header: 'Estado',
      sortable: true,
      accessor: (row) => <StatusBadge estado={row.estado} />,
    },
    {
      key: 'fecha',
      header: 'Fecha',
      sortable: true,
      accessor: (row) => row.creado_en.slice(0, 10),
    },
    {
      key: 'workflow',
      header: 'Workflow',
      sortable: false,
      className: 'w-48',
      accessor: (row) => (
        <TareaWorkflow
          tarea={row}
          onChangeEstado={handleChangeEstado}
          onDelegar={handleDelegar}
          isLoading={
            changeEstadoMutation.isPending ||
            delegarMutation.isPending
          }
        />
      ),
    },
  ]

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestión de tareas
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Seguimiento de tareas internas
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            + Nueva tarea
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
          <TareaForm
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
          <div className="mb-4 flex flex-wrap gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Estado
              </label>
              <select
                value={filters.estado ?? ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    estado: (e.target.value as TareaEstado) || undefined,
                  })
                }
                className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="">Todos</option>
                <option value="Pendiente">Pendiente</option>
                <option value="En progreso">En progreso</option>
                <option value="Resuelta">Resuelta</option>
                <option value="Cancelada">Cancelada</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Materia
              </label>
              <input
                type="text"
                value={filters.materia_id ?? ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    materia_id: e.target.value || undefined,
                  })
                }
                placeholder="ID materia..."
                className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          {activeTab === 'mis-tareas' && (
            <DataTable
              columns={columns}
              data={data ?? []}
              isLoading={isLoading}
              emptyMessage="No hay tareas."
              getRowKey={(row) => row.id}
            />
          )}

          {activeTab === 'administracion' && (
            <DataTable
              columns={columns}
              data={data ?? []}
              isLoading={isLoading}
              emptyMessage="No hay tareas con los filtros seleccionados."
              getRowKey={(row) => row.id}
            />
          )}
        </div>
      </div>
    </div>
  )
}
