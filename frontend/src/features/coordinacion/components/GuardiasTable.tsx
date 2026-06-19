import { useCallback } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { useGuardias } from '@/features/coordinacion/services/encuentros'
import type { Guardia } from '@/features/coordinacion/types'

interface GuardiasTableProps {
  filters?: Record<string, string>
}

export function GuardiasTable({ filters }: GuardiasTableProps) {
  const { data, isLoading } = useGuardias(filters)

  const handleExport = useCallback(() => {
    if (!data || data.length === 0) return
    const header =
      'Fecha\tMateria\tDocente cubierto\tTutor\tComentario\n'
    const rows = data
      .map(
        (g) =>
          `${g.fecha.slice(0, 10)}\t${g.materia_nombre ?? g.materia_id}\t${g.docente_cubierto_nombre ?? g.docente_cubierto_id}\t${g.tutor_nombre ?? g.tutor_id}\t${g.comentario ?? ''}`
      )
      .join('\n')
    const blob = new Blob([header + rows], {
      type: 'text/tab-separated-values',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `guardias-${new Date().toISOString().slice(0, 10)}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
  }, [data])

  const columns: Column<Guardia>[] = [
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
      key: 'docente',
      header: 'Docente cubierto',
      sortable: true,
      accessor: (row) =>
        row.docente_cubierto_nombre ?? row.docente_cubierto_id,
    },
    {
      key: 'tutor',
      header: 'Tutor',
      sortable: true,
      accessor: (row) => row.tutor_nombre ?? row.tutor_id,
    },
    {
      key: 'comentario',
      header: 'Comentario',
      sortable: false,
      accessor: (row) => (
        <span className="text-xs text-gray-500">
          {row.comentario ?? '—'}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleExport}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Exportar
        </button>
      </div>
      <DataTable
        columns={columns}
        data={data ?? []}
        isLoading={isLoading}
        emptyMessage="No hay guardias registradas."
        getRowKey={(row) => row.id}
      />
    </div>
  )
}
