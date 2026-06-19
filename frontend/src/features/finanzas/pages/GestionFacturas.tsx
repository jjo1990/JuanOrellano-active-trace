import { useState } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { FacturaDetalle } from '@/features/finanzas/components/FacturaDetalle'
import { useFacturas, useCambiarEstadoFactura } from '@/features/finanzas/services/facturas'
import type { Factura, FacturaFilters } from '@/features/finanzas/types'

export function GestionFacturas() {
  const [filters, setFilters] = useState<FacturaFilters>({})
  const [search, setSearch] = useState('')
  const [docente, setDocente] = useState('')
  const [estado, setEstado] = useState<'Pendiente' | 'Abonada' | ''>('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [confirmId, setConfirmId] = useState<string | null>(null)

  const activeFilters: FacturaFilters = {
    ...(docente ? { docente } : {}),
    ...(estado ? { estado } : {}),
    ...(fechaDesde ? { fecha_desde: fechaDesde } : {}),
    ...(fechaHasta ? { fecha_hasta: fechaHasta } : {}),
    ...(search ? { search } : {}),
  }

  const { data, isLoading } = useFacturas(activeFilters)
  const cambiarEstado = useCambiarEstadoFactura()

  const facturas = data ?? []

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(value)

  const columns: Column<Factura>[] = [
    {
      key: 'docente',
      header: 'Docente',
      sortable: true,
      accessor: (row) => row.docente_nombre,
    },
    {
      key: 'periodo',
      header: 'Período',
      sortable: true,
      accessor: (row) => row.periodo,
    },
    {
      key: 'fecha_carga',
      header: 'Fecha carga',
      sortable: true,
      accessor: (row) =>
        new Date(row.fecha_carga).toLocaleDateString('es-AR'),
    },
    {
      key: 'estado',
      header: 'Estado',
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.estado === 'Abonada'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {row.estado}
        </span>
      ),
    },
    {
      key: 'monto',
      header: 'Monto',
      sortable: true,
      accessor: (row) => (row.monto != null ? formatCurrency(row.monto) : '—'),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      accessor: (row) => (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() =>
              setExpandedId(expandedId === row.id ? null : row.id)
            }
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            {expandedId === row.id ? 'Ocultar' : 'Detalle'}
          </button>
          <button
            type="button"
            onClick={() => setConfirmId(row.id)}
            className={`text-xs ${
              row.estado === 'Pendiente'
                ? 'text-green-600 hover:text-green-800'
                : 'text-yellow-600 hover:text-yellow-800'
            }`}
          >
            {row.estado === 'Pendiente'
              ? 'Marcar abonada'
              : 'Revertir pendiente'}
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Gestión de facturas</h1>

      <div className="flex flex-wrap gap-4 rounded-lg border border-gray-200 bg-white p-4">
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Búsqueda
          </label>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Docente
          </label>
          <input
            type="text"
            value={docente}
            onChange={(e) => setDocente(e.target.value)}
            placeholder="Nombre docente"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Estado
          </label>
          <select
            value={estado}
            onChange={(e) =>
              setEstado(e.target.value as 'Pendiente' | 'Abonada' | '')
            }
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">Todos</option>
            <option value="Pendiente">Pendiente</option>
            <option value="Abonada">Abonada</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Fecha desde
          </label>
          <input
            type="date"
            value={fechaDesde}
            onChange={(e) => setFechaDesde(e.target.value)}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Fecha hasta
          </label>
          <input
            type="date"
            value={fechaHasta}
            onChange={(e) => setFechaHasta(e.target.value)}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  className={`px-4 py-3 text-left font-medium text-gray-700 ${
                    col.className ?? ''
                  }`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {isLoading && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-sm text-gray-500">
                  Cargando...
                </td>
              </tr>
            )}
            {!isLoading && facturas.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-sm text-gray-500">
                  No hay facturas disponibles.
                </td>
              </tr>
            )}
            {!isLoading &&
              facturas.map((factura) => (
                <tr key={factura.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-700">
                    {factura.docente_nombre}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">{factura.periodo}</td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {new Date(factura.fecha_carga).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        factura.estado === 'Abonada'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {factura.estado}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {factura.monto != null ? formatCurrency(factura.monto) : '—'}
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() =>
                          setExpandedId(
                            expandedId === factura.id ? null : factura.id
                          )
                        }
                        className="text-xs text-indigo-600 hover:text-indigo-800"
                      >
                        {expandedId === factura.id ? 'Ocultar' : 'Detalle'}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          const nuevoEstado =
                            factura.estado === 'Pendiente'
                              ? 'Abonada'
                              : 'Pendiente'
                          cambiarEstado.mutate({
                            id: factura.id,
                            estado: nuevoEstado,
                          })
                        }}
                        className={`text-xs ${
                          factura.estado === 'Pendiente'
                            ? 'text-green-600 hover:text-green-800'
                            : 'text-yellow-600 hover:text-yellow-800'
                        }`}
                      >
                        {factura.estado === 'Pendiente'
                          ? 'Marcar abonada'
                          : 'Revertir pendiente'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
