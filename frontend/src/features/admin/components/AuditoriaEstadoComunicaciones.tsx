import { useEstadoComunicaciones } from '@/features/admin/services/auditoria'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type {
  AuditoriaFilters,
  EstadoComunicacionesItem,
} from '@/features/admin/types'

interface AuditoriaEstadoComunicacionesProps {
  filters: AuditoriaFilters
}

export function AuditoriaEstadoComunicaciones({
  filters,
}: AuditoriaEstadoComunicacionesProps) {
  const { data, isLoading } = useEstadoComunicaciones(filters)

  const columns: Column<EstadoComunicacionesItem>[] = [
    {
      key: 'docente',
      header: 'Docente',
      sortable: true,
      accessor: (row) => row.docente_nombre,
    },
    {
      key: 'materia',
      header: 'Materia',
      sortable: true,
      accessor: (row) => row.materia_nombre,
    },
    {
      key: 'pendientes',
      header: 'Pendientes',
      accessor: (row) => row.pendientes,
    },
    {
      key: 'enviados',
      header: 'Enviados',
      accessor: (row) => row.enviados,
    },
    {
      key: 'fallidos',
      header: 'Fallidos',
      accessor: (row) => row.fallidos,
    },
    {
      key: 'cancelados',
      header: 'Cancelados',
      accessor: (row) => row.cancelados,
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      getRowKey={(row) => `${row.docente_id}-${row.materia_id}`}
      emptyMessage="No hay datos de comunicación para los filtros seleccionados."
    />
  )
}
