import { useState, useCallback } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useMonitorPorDocente } from '@/features/coordinacion/services/monitores'
import type { MonitorDocenteEntry } from '@/features/coordinacion/types'

export function MonitorPorDocente() {
  const [docenteId, setDocenteId] = useState('')

  const { data, isLoading } = useMonitorPorDocente(docenteId)

  const handleExport = useCallback(() => {
    if (!data || data.length === 0) return
    const header =
      'Alumno\tEmail\tMateria\tComisión\tActividades\tEstado\n'
    const rows = data
      .map(
        (m) =>
          `${m.alumno_nombre}\t${m.email}\t${m.materia_nombre}\t${m.comision_nombre}\t${m.actividades_completadas}/${m.actividades_totales}\t${m.estado}`
      )
      .join('\n')
    const blob = new Blob([header + rows], {
      type: 'text/tab-separated-values',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `monitor-docente-${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  }, [data])

  const columns: Column<MonitorDocenteEntry>[] = [
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
      key: 'materia',
      header: 'Materia',
      sortable: true,
      accessor: (row) => row.materia_nombre,
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
      accessor: (row) => <StatusBadge estado={row.estado} />,
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-gray-200 bg-white p-4">
        <div className="min-w-0 flex-1">
          <label className="block text-xs font-medium text-gray-500">
            Docente ID
          </label>
          <input
            type="text"
            value={docenteId}
            onChange={(e) => setDocenteId(e.target.value)}
            placeholder="ID de docente..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
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
        emptyMessage={
          docenteId
            ? 'No se encontraron alumnos para este docente.'
            : 'Ingresá un ID de docente para ver sus alumnos.'
        }
        getRowKey={(row) => row.alumno_id}
      />
    </div>
  )
}
