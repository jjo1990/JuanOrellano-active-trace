import { useState, useCallback } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import {
  useFechasAcademicas,
  useDeleteFechaAcademica,
} from '@/features/coordinacion/services/programas'
import type {
  FechaAcademica,
} from '@/features/coordinacion/types'

interface FechasAcademicasTableProps {
  cohorteId: string
}

export function FechasAcademicasTable({ cohorteId }: FechasAcademicasTableProps) {
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data, isLoading } = useFechasAcademicas(cohorteId || undefined)
  const deleteMutation = useDeleteFechaAcademica()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleDelete = useCallback(
    (id: string) => {
      if (!window.confirm('¿Eliminar esta fecha?')) return
      deleteMutation.mutate(id, {
        onSuccess: () => showMessage('Fecha eliminada.', 'success'),
        onError: () => showMessage('Error al eliminar.', 'error'),
      })
    },
    [deleteMutation, showMessage]
  )

  const columns: Column<FechaAcademica>[] = [
    {
      key: 'fecha',
      header: 'Fecha',
      sortable: true,
      accessor: (row) => row.fecha.slice(0, 10),
    },
    {
      key: 'materia',
      header: 'Materia',
      sortable: true,
      accessor: (row) => row.materia_nombre ?? row.materia_id,
    },
    {
      key: 'tipo',
      header: 'Tipo',
      sortable: true,
      accessor: (row) => (
        <span className="inline-flex items-center rounded-full bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
          {row.tipo}
          {row.numero != null ? ` #${row.numero}` : ''}
        </span>
      ),
    },
    {
      key: 'comentario',
      header: 'Comentario',
      sortable: false,
      accessor: (row) => (
        <span className="text-xs text-gray-400">
          {row.comentario ?? '—'}
        </span>
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
    <div className="space-y-4">
      {message && (
        <div
          className={`rounded-md px-4 py-3 text-sm ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      <DataTable
        columns={columns}
        data={data ?? []}
        isLoading={isLoading}
        emptyMessage="No hay fechas académicas registradas."
        getRowKey={(row) => row.id}
      />
    </div>
  )
}
