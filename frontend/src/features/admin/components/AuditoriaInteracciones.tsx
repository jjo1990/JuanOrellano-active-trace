import { useInteracciones } from '@/features/admin/services/auditoria'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type { AuditoriaFilters, InteraccionesItem } from '@/features/admin/types'

interface AuditoriaInteraccionesProps {
  filters: AuditoriaFilters
}

export function AuditoriaInteracciones({
  filters,
}: AuditoriaInteraccionesProps) {
  const { data, isLoading } = useInteracciones(filters)

  const columns: Column<InteraccionesItem>[] = [
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
      key: 'analisis',
      header: 'Análisis',
      accessor: (row) => row.analisis_desempeno,
    },
    {
      key: 'vistas',
      header: 'Vistas previas',
      accessor: (row) => row.vista_previa,
    },
    {
      key: 'importaciones',
      header: 'Import.',
      accessor: (row) => row.importaciones,
    },
    {
      key: 'envios',
      header: 'Envíos',
      accessor: (row) => row.envios,
    },
    {
      key: 'limpieza',
      header: 'Limpieza',
      accessor: (row) => row.limpieza_datos,
    },
    {
      key: 'umbral',
      header: 'Umbral',
      accessor: (row) => row.config_umbral,
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={data ?? []}
      isLoading={isLoading}
      getRowKey={(row) => `${row.docente_id}-${row.materia_id}`}
      emptyMessage="No hay métricas de interacciones para los filtros seleccionados."
    />
  )
}
