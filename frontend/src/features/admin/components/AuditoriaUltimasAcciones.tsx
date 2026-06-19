import { useUltimasAcciones } from '@/features/admin/services/auditoria'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type { AuditoriaFilters, AuditoriaEntry } from '@/features/admin/types'

interface AuditoriaUltimasAccionesProps {
  filters: AuditoriaFilters
}

export function AuditoriaUltimasAcciones({
  filters,
}: AuditoriaUltimasAccionesProps) {
  const { data, isLoading } = useUltimasAcciones(filters)

  const columns: Column<AuditoriaEntry>[] = [
    {
      key: 'fecha',
      header: 'Fecha',
      sortable: true,
      accessor: (row) =>
        new Date(row.fecha).toLocaleString('es-AR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        }),
    },
    {
      key: 'usuario',
      header: 'Usuario',
      sortable: true,
      accessor: (row) => row.usuario_nombre ?? row.usuario_id,
    },
    {
      key: 'materia',
      header: 'Materia',
      accessor: (row) => row.materia_nombre ?? row.materia_id ?? '—',
    },
    {
      key: 'tipo_accion',
      header: 'Acción',
      sortable: true,
      accessor: (row) => row.tipo_accion,
    },
    {
      key: 'registros',
      header: 'Registros',
      accessor: (row) => row.registros_afectados,
    },
    {
      key: 'ip',
      header: 'IP',
      accessor: (row) => row.ip ?? '—',
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      getRowKey={(row) => row.id}
      emptyMessage="No hay registros de auditoría recientes."
    />
  )
}
