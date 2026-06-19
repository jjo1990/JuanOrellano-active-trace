import { useState, useCallback, useEffect, useRef } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useMonitorGeneral } from '@/features/coordinacion/services/monitores'
import type {
  MonitorGeneralEntry,
  MonitorGeneralFilters,
} from '@/features/coordinacion/types'

export function MonitorGeneralTable() {
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState<MonitorGeneralFilters>({})
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setFilters((prev) => ({
        ...prev,
        search: search || undefined,
      }))
    }, 300)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [search])

  const { data, isLoading } = useMonitorGeneral(filters)

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
    a.download = `monitor-general-${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  }, [data])

  const columns: Column<MonitorGeneralEntry>[] = [
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

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-gray-200 bg-white p-4">
        <div className="min-w-0 flex-1">
          <label className="block text-xs font-medium text-gray-500">
            Buscar alumno
          </label>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Nombre o apellido..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div className="min-w-0 flex-1">
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
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div className="min-w-0 flex-1">
          <label className="block text-xs font-medium text-gray-500">
            Comisión
          </label>
          <input
            type="text"
            value={filters.comision_id ?? ''}
            onChange={(e) =>
              setFilters({
                ...filters,
                comision_id: e.target.value || undefined,
              })
            }
            placeholder="ID comisión..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div className="min-w-0 flex-1">
          <label className="block text-xs font-medium text-gray-500">
            Estado
          </label>
          <select
            value={filters.estado ?? ''}
            onChange={(e) =>
              setFilters({
                ...filters,
                estado: e.target.value || undefined,
              })
            }
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">Todos</option>
            <option value="Atrasado">Atrasado</option>
            <option value="Al día">Al día</option>
            <option value="Sin datos">Sin datos</option>
          </select>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleExport}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Exportar
          </button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data ?? []}
        isLoading={isLoading}
        emptyMessage="No se encontraron alumnos con los filtros aplicados."
        getRowKey={(row) => row.alumno_id}
      />
    </div>
  )
}
