import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useNotasFinales } from '@/features/academico/services/analisis'
import type { NotaFinal } from '@/features/academico/types'

interface NotasFinalesTableProps {
  materiaId: string
}

const columns: Column<NotaFinal>[] = [
  {
    key: 'alumno',
    header: 'Alumno',
    sortable: true,
    accessor: (row) => row.alumno_nombre,
  },
  {
    key: 'nota',
    header: 'Nota Final',
    sortable: true,
    accessor: (row) => row.nota_final.toFixed(1),
  },
  {
    key: 'estado',
    header: 'Estado',
    sortable: true,
    accessor: (row) => <StatusBadge estado={row.estado} />,
  },
]

export function NotasFinalesTable({ materiaId }: NotasFinalesTableProps) {
  const { data, isLoading } = useNotasFinales(materiaId)

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      emptyMessage="No hay notas finales calculadas. Import\u00E1 calificaciones primero."
      getRowKey={(row) => row.alumno_id}
    />
  )
}
