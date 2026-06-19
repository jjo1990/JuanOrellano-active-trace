import { useState } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type { LiquidacionEntry } from '@/features/finanzas/types'

interface LiquidacionTableProps {
  entries: LiquidacionEntry[]
  isLoading?: boolean
}

export function LiquidacionTable({
  entries,
  isLoading,
}: LiquidacionTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(value)

  const columns: Column<LiquidacionEntry>[] = [
    {
      key: 'docente',
      header: 'Docente',
      sortable: true,
      accessor: (row) => row.docente_nombre,
    },
    {
      key: 'rol',
      header: 'Rol',
      accessor: (row) => row.rol,
    },
    {
      key: 'materias',
      header: 'Materias',
      accessor: (row) => row.materias.join(', '),
    },
    {
      key: 'salario_base',
      header: 'Salario Base',
      sortable: true,
      accessor: (row) => formatCurrency(row.salario_base),
    },
    {
      key: 'plus',
      header: 'Plus',
      accessor: (row) => {
        const totalPlus = row.plus.reduce((sum, p) => sum + p.monto, 0)
        return formatCurrency(totalPlus)
      },
    },
    {
      key: 'total',
      header: 'Total',
      sortable: true,
      accessor: (row) => formatCurrency(row.total),
    },
  ]

  return (
    <DataTable
      columns={columns}
      data={entries}
      isLoading={isLoading}
      getRowKey={(row) => row.id}
      emptyMessage="No hay liquidaciones para este segmento."
    />
  )
}
