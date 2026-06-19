import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useHistorial } from '@/features/finanzas/services/liquidaciones'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type { LiquidacionCerrada } from '@/features/finanzas/types'

export function HistorialLiquidaciones() {
  const navigate = useNavigate()
  const [cohorteId, setCohorteId] = useState('')
  const [mes, setMes] = useState<number | undefined>()
  const [anio, setAnio] = useState<number | undefined>()

  const { data, isLoading } = useHistorial(cohorteId || undefined, mes, anio)

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(value)

  const columns: Column<LiquidacionCerrada>[] = [
    {
      key: 'cohorte',
      header: 'Cohorte',
      sortable: true,
      accessor: (row) => row.cohorte_nombre,
    },
    {
      key: 'periodo',
      header: 'Período',
      sortable: true,
      accessor: (row) => `${row.mes}/${row.anio}`,
    },
    {
      key: 'fecha_cierre',
      header: 'Fecha de cierre',
      sortable: true,
      accessor: (row) =>
        new Date(row.fecha_cierre).toLocaleDateString('es-AR'),
    },
    {
      key: 'total',
      header: 'Total liquidado',
      sortable: true,
      accessor: (row) => formatCurrency(row.total_liquidado),
    },
    {
      key: 'docentes',
      header: 'Docentes',
      accessor: (row) => row.cantidad_docentes,
    },
  ]

  const liquidaciones = data ?? []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Historial de liquidaciones
      </h1>

      <div className="flex gap-4 rounded-lg border border-gray-200 bg-white p-4">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-500">
            Cohorte
          </label>
          <input
            type="text"
            value={cohorteId}
            onChange={(e) => setCohorteId(e.target.value)}
            placeholder="ID de cohorte"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Mes
          </label>
          <select
            value={mes ?? ''}
            onChange={(e) =>
              setMes(e.target.value ? Number(e.target.value) : undefined)
            }
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">Todos</option>
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Año
          </label>
          <input
            type="number"
            value={anio ?? ''}
            onChange={(e) =>
              setAnio(e.target.value ? Number(e.target.value) : undefined)
            }
            placeholder="Año"
            className="mt-1 block w-24 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <DataTable
        columns={columns}
        data={liquidaciones}
        isLoading={isLoading}
        getRowKey={(row) => row.id}
        emptyMessage="No hay liquidaciones cerradas para este período."
      />
    </div>
  )
}
