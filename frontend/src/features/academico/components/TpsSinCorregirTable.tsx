import { DataTable, type Column } from '@/shared/components/DataTable'
import { useTpsSinCorregir } from '@/features/academico/services/analisis'
import type { TpSinCorregir } from '@/features/academico/types'

interface TpsSinCorregirTableProps {
  materiaId: string
}

const columns: Column<TpSinCorregir>[] = [
  {
    key: 'alumno',
    header: 'Alumno',
    sortable: true,
    accessor: (row) => row.alumno_nombre,
  },
  {
    key: 'actividad',
    header: 'Actividad',
    sortable: true,
    accessor: (row) => row.actividad_nombre,
  },
  {
    key: 'fecha',
    header: 'Fecha entrega',
    sortable: true,
    accessor: (row) => row.fecha_entrega ?? 'Sin fecha',
  },
  {
    key: 'estado',
    header: 'Estado',
    sortable: true,
    accessor: (row) => row.estado,
  },
]

export function TpsSinCorregirTable({ materiaId }: TpsSinCorregirTableProps) {
  const { data, isLoading } = useTpsSinCorregir(materiaId)

  const handleExport = () => {
    if (!data || data.length === 0) return

    const header = 'Alumno\tActividad\tFecha entrega\tEstado\n'
    const rows = data
      .map(
        (tp) =>
          `${tp.alumno_nombre}\t${tp.actividad_nombre}\t${tp.fecha_entrega ?? 'Sin fecha'}\t${tp.estado}`
      )
      .join('\n')

    const blob = new Blob([header + rows], {
      type: 'text/tab-separated-values',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'tps-sin-corregir.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  }

  const hasData = data && data.length > 0

  return (
    <div className="space-y-3">
      {hasData && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={handleExport}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <span className="flex items-center gap-1.5">
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
                />
              </svg>
              Exportar TPs sin corregir
            </span>
          </button>
        </div>
      )}

      <DataTable
        columns={columns}
        data={data ?? []}
        isLoading={isLoading}
        emptyMessage="No hay TPs pendientes de correcci\u00F3n."
        getRowKey={(row) => `${row.alumno_id}-${row.actividad_id}`}
      />
    </div>
  )
}
