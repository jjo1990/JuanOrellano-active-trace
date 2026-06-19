import { DataTable, type Column } from '@/shared/components/DataTable'
import { StatusBadge } from '@/shared/components/StatusBadge'
import { useHistorialComunicaciones } from '@/features/academico/services/comunicaciones'
import type { ComunicacionLote } from '@/features/academico/types'

interface HistorialComunicacionesProps {
  materiaId: string
}

const columns: Column<ComunicacionLote>[] = [
  {
    key: 'fecha',
    header: 'Fecha',
    sortable: true,
    accessor: (row) =>
      new Date(row.creado_en).toLocaleString('es-AR'),
  },
  {
    key: 'destinatarios',
    header: 'Destinatarios',
    sortable: true,
    accessor: (row) => row.total_destinatarios,
  },
  {
    key: 'progreso',
    header: 'Progreso',
    accessor: (row) =>
      `${row.enviados}/${row.total_destinatarios}${row.errores > 0 ? ` (${row.errores} errores)` : ''}`,
  },
  {
    key: 'estado',
    header: 'Estado',
    sortable: true,
    accessor: (row) => <StatusBadge estado={row.estado} />,
  },
]

export function HistorialComunicaciones({
  materiaId,
}: HistorialComunicacionesProps) {
  const { data, isLoading } = useHistorialComunicaciones(materiaId)

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      emptyMessage="No se han enviado comunicaciones para esta materia."
      getRowKey={(row) => row.id}
    />
  )
}
