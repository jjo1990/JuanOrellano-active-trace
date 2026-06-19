import { useState, useCallback } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { AvisoForm } from '@/features/coordinacion/components/AvisoForm'
import { AvisoAcknowledgments } from '@/features/coordinacion/components/AvisoAcknowledgments'
import {
  useAvisos,
  useCreateAviso,
  useUpdateAviso,
  useDeleteAviso,
} from '@/features/coordinacion/services/avisos'
import type { Aviso, AvisoFormValues } from '@/features/coordinacion/types'

export function GestionAvisos() {
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Aviso | null>(null)
  const [selectedAvisoId, setSelectedAvisoId] = useState<string | null>(null)
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data, isLoading } = useAvisos()
  const createMutation = useCreateAviso()
  const updateMutation = useUpdateAviso()
  const deleteMutation = useDeleteAviso()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleCreate = useCallback(
    (formData: AvisoFormValues) => {
      createMutation.mutate(formData, {
        onSuccess: () => {
          showMessage('Aviso creado.', 'success')
          setShowForm(false)
        },
        onError: () => showMessage('Error al crear aviso.', 'error'),
      })
    },
    [createMutation, showMessage]
  )

  const handleUpdate = useCallback(
    (formData: AvisoFormValues) => {
      if (!editing) return
      updateMutation.mutate(
        { id: editing.id, data: formData },
        {
          onSuccess: () => {
            showMessage('Aviso actualizado.', 'success')
            setShowForm(false)
            setEditing(null)
          },
          onError: () => showMessage('Error al actualizar aviso.', 'error'),
        }
      )
    },
    [editing, updateMutation, showMessage]
  )

  const handleDelete = useCallback(
    (id: string) => {
      if (!window.confirm('¿Eliminar este aviso?')) return
      deleteMutation.mutate(id, {
        onSuccess: () => showMessage('Aviso eliminado.', 'success'),
        onError: () => showMessage('Error al eliminar aviso.', 'error'),
      })
    },
    [deleteMutation, showMessage]
  )

  const severidadVariant: Record<string, string> = {
    Baja: 'bg-blue-100 text-blue-800',
    Media: 'bg-yellow-100 text-yellow-800',
    Alta: 'bg-orange-100 text-orange-800',
    Urgente: 'bg-red-100 text-red-800',
  }

  const columns: Column<Aviso>[] = [
    {
      key: 'titulo',
      header: 'Título',
      sortable: true,
      accessor: (row) => row.titulo,
    },
    {
      key: 'scope',
      header: 'Scope',
      sortable: true,
      accessor: (row) => (
        <span className="text-xs text-gray-500">{row.scope}</span>
      ),
    },
    {
      key: 'severidad',
      header: 'Severidad',
      sortable: true,
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            severidadVariant[row.severidad] ?? 'bg-gray-100 text-gray-700'
          }`}
        >
          {row.severidad}
        </span>
      ),
    },
    {
      key: 'vigencia',
      header: 'Vigencia',
      sortable: false,
      accessor: (row) => (
        <span className="text-xs text-gray-500">
          {row.fecha_inicio.slice(0, 10)} → {row.fecha_fin.slice(0, 10)}
        </span>
      ),
    },
    {
      key: 'ack',
      header: 'Ack',
      sortable: false,
      accessor: (row) =>
        row.requiere_ack ? (
          <button
            type="button"
            onClick={() => setSelectedAvisoId(row.id)}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            Ver confirmaciones
          </button>
        ) : (
          <span className="text-xs text-gray-400">—</span>
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
            onClick={() => {
              setEditing(row)
              setShowForm(true)
            }}
            className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => handleDelete(row.id)}
            className="text-xs font-medium text-red-600 hover:text-red-800"
          >
            Eliminar
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
              Gestión de avisos
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Publicá avisos para alumnos, docentes o toda la institución
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              setEditing(null)
              setShowForm(true)
            }}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            + Nuevo aviso
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
          <AvisoForm
            initialValues={
              editing
                ? {
                    titulo: editing.titulo,
                    cuerpo: editing.cuerpo,
                    scope: editing.scope,
                    scope_materia_id: editing.scope_materia_id,
                    scope_cohorte_id: editing.scope_cohorte_id,
                    scope_rol: editing.scope_rol,
                    severidad: editing.severidad,
                    fecha_inicio: editing.fecha_inicio.slice(0, 10),
                    fecha_fin: editing.fecha_fin.slice(0, 10),
                    requiere_ack: editing.requiere_ack,
                  }
                : undefined
            }
            onSubmit={editing ? handleUpdate : handleCreate}
            isLoading={
              editing
                ? updateMutation.isPending
                : createMutation.isPending
            }
            onCancel={() => {
              setShowForm(false)
              setEditing(null)
            }}
          />
        </div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <DataTable
          columns={columns}
          data={data ?? []}
          isLoading={isLoading}
          emptyMessage="No hay avisos publicados."
          getRowKey={(row) => row.id}
        />
      </div>

      {selectedAvisoId && (
        <AvisoAcknowledgments
          avisoId={selectedAvisoId}
          onClose={() => setSelectedAvisoId(null)}
        />
      )}
    </div>
  )
}
