import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { type EquipoEntry } from '@/features/coordinacion/types'

interface EquiposTableProps {
  data: EquipoEntry[]
  isLoading: boolean
  onModificarVigencia: (entry: EquipoEntry) => void
}

const columns = (onModificar: (entry: EquipoEntry) => void): Column<EquipoEntry>[] => [
  {
    key: 'docente',
    header: 'Docente',
    sortable: true,
    accessor: (row) => row.docente_nombre,
  },
  {
    key: 'rol',
    header: 'Rol',
    sortable: true,
    accessor: (row) => row.rol,
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
    key: 'vigencia',
    header: 'Vigencia',
    sortable: false,
    accessor: (row) => (
      <span className="text-xs text-gray-500">
        {row.fecha_inicio.slice(0, 10)} → {row.fecha_fin?.slice(0, 10) ?? '—'}
      </span>
    ),
  },
  {
    key: 'estado',
    header: 'Estado',
    sortable: true,
    accessor: (row) => (
      <StatusBadge estado={row.activo ? 'Al día' : 'Cancelado'} />
    ),
  },
  {
    key: 'acciones',
    header: 'Acciones',
    sortable: false,
    className: 'text-right',
    accessor: (row) => (
      <button
        type="button"
        onClick={() => onModificar(row)}
        className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
      >
        Modificar vigencia
      </button>
    ),
  },
]

export function EquiposTable({
  data,
  isLoading,
  onModificarVigencia,
}: EquiposTableProps) {
  return (
    <DataTable
      columns={columns(onModificarVigencia)}
      data={data}
      isLoading={isLoading}
      emptyMessage="No hay asignaciones docentes para los filtros seleccionados."
      getRowKey={(row) => row.id}
    />
  )
}
