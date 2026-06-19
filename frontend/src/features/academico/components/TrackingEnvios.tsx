import { useEstadoEnvio } from '@/features/academico/services/comunicaciones'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type { ComunicacionEnvio } from '@/features/academico/types'

interface TrackingEnviosProps {
  loteId: string | null
}

const columns: Column<ComunicacionEnvio>[] = [
  {
    key: 'alumno',
    header: 'Alumno',
    sortable: true,
    accessor: (row) => row.alumno_nombre,
  },
  {
    key: 'email',
    header: 'Email',
    sortable: true,
    accessor: (row) => row.email,
  },
  {
    key: 'estado',
    header: 'Estado',
    sortable: true,
    accessor: (row) => (
      <div className="flex items-center gap-2">
        <StatusBadge estado={row.estado} />
        {row.error_motivo && (
          <span
            className="cursor-help text-xs text-red-500"
            title={row.error_motivo}
          >
            ?
          </span>
        )}
      </div>
    ),
  },
  {
    key: 'fecha',
    header: 'Fecha envío',
    sortable: true,
    accessor: (row) =>
      row.enviado_en
        ? new Date(row.enviado_en).toLocaleString('es-AR')
        : '\u2014',
  },
]

export function TrackingEnvios({ loteId }: TrackingEnviosProps) {
  const { data, isLoading, isFetching } = useEstadoEnvio(loteId)

  if (!loteId) {
    return (
      <p className="py-8 text-center text-sm text-gray-400">
        Enviá una comunicación para ver el tracking en tiempo real.
      </p>
    )
  }

  const completados = data?.filter((e) => e.estado === 'Enviado').length ?? 0
  const errores = data?.filter((e) => e.estado === 'Error').length ?? 0
  const total = data?.length ?? 0

  return (
    <div className="space-y-3">
      {total > 0 && (
        <div className="mb-3 grid grid-cols-3 gap-4">
          <div className="rounded-md bg-gray-50 p-3 text-center">
            <p className="text-xs text-gray-500">Total</p>
            <p className="text-lg font-semibold text-gray-900">{total}</p>
          </div>
          <div className="rounded-md bg-green-50 p-3 text-center">
            <p className="text-xs text-green-600">Enviados</p>
            <p className="text-lg font-semibold text-green-700">{completados}</p>
          </div>
          <div className="rounded-md bg-red-50 p-3 text-center">
            <p className="text-xs text-red-600">Errores</p>
            <p className="text-lg font-semibold text-red-700">{errores}</p>
          </div>
        </div>
      )}

      {isFetching && !isLoading && (
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <div className="h-3 w-3 animate-spin rounded-full border border-indigo-600 border-t-transparent" />
          Actualizando...
        </div>
      )}

      <DataTable
        columns={columns}
        data={data ?? []}
        isLoading={isLoading}
        emptyMessage="Esperando datos de tracking..."
        getRowKey={(row) => row.id}
      />
    </div>
  )
}
