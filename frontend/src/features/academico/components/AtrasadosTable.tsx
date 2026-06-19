import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useAtrasados } from '@/features/academico/services/analisis'
import type { Atrasado } from '@/features/academico/types'

interface AtrasadosTableProps {
  materiaId: string
}

const columns: Column<Atrasado>[] = [
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

export function AtrasadosTable({ materiaId }: AtrasadosTableProps) {
  const { data, isLoading } = useAtrasados(materiaId)

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      emptyMessage="No hay alumnos atrasados. \u00A1Buen trabajo!"
      getRowKey={(row) => row.alumno_id}
    />
  )
}
