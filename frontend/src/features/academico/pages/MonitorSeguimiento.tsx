import { useState, useCallback } from 'react'
import { MonitorFilters } from '@/features/academico/components/MonitorFilters'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useMonitor } from '@/features/academico/services/analisis'
import type {
  MonitorEntry,
  MonitorFilters as MonitorFiltersType,
} from '@/features/academico/types'

const columns: Column<MonitorEntry>[] = [
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
    key: 'comision',
    header: 'Comisión',
    sortable: true,
    accessor: (row) => row.comision_nombre,
  },
  {
    key: 'actividades',
    header: 'Actividades',
    sortable: true,
    accessor: (row) =>
      `${row.actividades_completadas}/${row.actividades_totales}`,
  },
  {
    key: 'estado',
    header: 'Estado',
    sortable: true,
    accessor: (row) => <StatusBadge estado={row.estado_general} />,
  },
]

export function MonitorSeguimiento() {
  const [filters, setFilters] = useState<MonitorFiltersType>({})
  const { data, isLoading } = useMonitor(filters)

  const handleFiltersChange = useCallback(
    (newFilters: MonitorFiltersType) => {
      setFilters(newFilters)
    },
    []
  )

  const handleExport = useCallback(() => {
    if (!data || data.length === 0) return

    const header =
      'Alumno\tEmail\tComisión\tActividades\tEstado\n'
    const rows = data
      .map(
        (m) =>
          `${m.alumno_nombre}\t${m.email}\t${m.comision_nombre}\t${m.actividades_completadas}/${m.actividades_totales}\t${m.estado_general}`
      )
      .join('\n')

    const blob = new Blob([header + rows], {
      type: 'text/tab-separated-values',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `monitor-seguimiento-${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  }, [data])

  const hasData = data && data.length > 0

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Monitor de seguimiento
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Estado de actividades de alumnos asignados
            </p>
          </div>

          {hasData && (
            <button
              type="button"
              onClick={handleExport}
              className="flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
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
              Exportar
            </button>
          )}
        </div>
      </div>

      <div className="mb-4">
        <MonitorFilters filters={filters} onChange={handleFiltersChange} />
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <DataTable
          columns={columns}
          data={data ?? []}
          isLoading={isLoading}
          emptyMessage="No se encontraron alumnos con los filtros seleccionados."
          getRowKey={(row) => row.alumno_id}
        />
      </div>
    </div>
  )
}
