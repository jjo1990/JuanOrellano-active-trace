import { DataTable, type Column } from '@/shared/components/DataTable'
import { useRanking } from '@/features/academico/services/analisis'
import type { RankingEntry } from '@/features/academico/types'

interface RankingTableProps {
  materiaId: string
}

const columns: Column<RankingEntry>[] = [
  {
    key: 'alumno',
    header: 'Alumno',
    sortable: true,
    accessor: (row) => row.alumno_nombre,
  },
  {
    key: 'aprobadas',
    header: 'Aprobadas',
    sortable: true,
    accessor: (row) => row.aprobadas,
  },
  {
    key: 'promedio',
    header: 'Promedio',
    sortable: true,
    accessor: (row) => row.promedio.toFixed(1),
  },
]

export function RankingTable({ materiaId }: RankingTableProps) {
  const { data, isLoading } = useRanking(materiaId)

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      emptyMessage="No hay datos de ranking para esta materia."
      getRowKey={(row) => row.alumno_id}
    />
  )
}
