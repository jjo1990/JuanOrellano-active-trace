import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useAtrasados } from '@/features/academico/services/analisis'
import type { Atrasado } from '@/features/academico/types'

interface SeleccionDestinatariosProps {
  materiaId: string
  selected: string[]
  onToggle: (id: string) => void
  onSelectAll: () => void
  onDeselectAll: () => void
}

export function SeleccionDestinatarios({
  materiaId,
  selected,
  onToggle,
  onSelectAll,
  onDeselectAll,
}: SeleccionDestinatariosProps) {
  const { data, isLoading } = useAtrasados(materiaId)
  const atrasados = data ?? []
  const allSelected = atrasados.length > 0 && selected.length === atrasados.length

  const columns: Column<Atrasado>[] = [
    {
      key: 'select',
      header: (
        <input
          type="checkbox"
          checked={allSelected}
          onChange={() => (allSelected ? onDeselectAll() : onSelectAll())}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
      ),
      accessor: (row) => (
        <input
          type="checkbox"
          checked={selected.includes(row.alumno_id)}
          onChange={() => onToggle(row.alumno_id)}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
      ),
    },
    {
      key: 'alumno',
      header: 'Alumno',
      sortable: true,
      accessor: (row) => row.alumno_nombre,
    },
    {
      key: 'pendientes',
      header: 'Act. pendientes',
      sortable: true,
      accessor: (row) => row.actividades_pendientes,
    },
    {
      key: 'promedio',
      header: 'Nota promedio',
      sortable: true,
      accessor: (row) => row.nota_promedio.toFixed(1),
    },
    {
      key: 'estado',
      header: 'Estado',
      sortable: true,
      accessor: (row) => <StatusBadge estado={row.estado} />,
    },
  ]

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">
          {selected.length} de {atrasados.length} seleccionados
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={onSelectAll}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            Seleccionar todos
          </button>
          <button
            type="button"
            onClick={onDeselectAll}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            Deseleccionar todos
          </button>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={atrasados}
        isLoading={isLoading}
        emptyMessage="No hay alumnos atrasados para comunicar."
        getRowKey={(row) => row.alumno_id}
      />
    </div>
  )
}
