import { useState, useCallback } from 'react'
import { useAuditoriaLog } from '@/features/admin/services/auditoria'
import { DataTable, type Column } from '@/shared/components/DataTable'
import type { AuditoriaFilters, AuditoriaEntry } from '@/features/admin/types'

export function LogAuditoria() {
  const [page, setPage] = useState(1)
  const [sort, setSort] = useState('fecha')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [usuarioId, setUsuarioId] = useState('')
  const [tipoAccion, setTipoAccion] = useState('')
  const [ip, setIp] = useState('')

  const filters: AuditoriaFilters = {
    ...(fechaDesde ? { fecha_desde: fechaDesde } : {}),
    ...(fechaHasta ? { fecha_hasta: fechaHasta } : {}),
    ...(materiaId ? { materia_id: materiaId } : {}),
    ...(usuarioId ? { usuario_id: usuarioId } : {}),
    ...(tipoAccion ? { tipo_accion: tipoAccion } : {}),
    ...(ip ? { ip } : {}),
  }

  const { data, isLoading } = useAuditoriaLog(filters, page, sort, order)

  const logEntries = data?.items ?? []
  const total = data?.total ?? 0
  const perPage = 50
  const totalPages = Math.max(1, Math.ceil(total / perPage))

  const limpiarFiltros = () => {
    setFechaDesde('')
    setFechaHasta('')
    setMateriaId('')
    setUsuarioId('')
    setTipoAccion('')
    setIp('')
    setPage(1)
  }

  const handleSort = useCallback(
    (column: string) => {
      if (sort === column) {
        setOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'))
      } else {
        setSort(column)
        setOrder('desc')
      }
    },
    [sort]
  )

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
          second: '2-digit',
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
      sortable: true,
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
      sortable: true,
      accessor: (row) => row.registros_afectados,
    },
    {
      key: 'ip',
      header: 'IP',
      accessor: (row) => row.ip ?? '—',
    },
    {
      key: 'user_agent',
      header: 'User Agent',
      accessor: (row) => {
        const ua = row.user_agent ?? '—'
        if (ua.length > 60) return ua.slice(0, 57) + '...'
        return ua
      },
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Log completo de auditoría
      </h1>

      <div className="flex flex-wrap items-end gap-4 rounded-lg border border-gray-200 bg-white p-4">
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Fecha desde
          </label>
          <input
            type="date"
            value={fechaDesde}
            onChange={(e) => { setFechaDesde(e.target.value); setPage(1) }}
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
            onChange={(e) => { setFechaHasta(e.target.value); setPage(1) }}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Materia
          </label>
          <input
            type="text"
            value={materiaId}
            onChange={(e) => { setMateriaId(e.target.value); setPage(1) }}
            placeholder="ID de materia"
            className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Usuario
          </label>
          <input
            type="text"
            value={usuarioId}
            onChange={(e) => { setUsuarioId(e.target.value); setPage(1) }}
            placeholder="ID de usuario"
            className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Tipo acción
          </label>
          <select
            value={tipoAccion}
            onChange={(e) => { setTipoAccion(e.target.value); setPage(1) }}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">Todas</option>
            <option value="importacion">Importación</option>
            <option value="envio">Envío</option>
            <option value="consulta">Consulta</option>
            <option value="configuracion">Configuración</option>
            <option value="login">Login</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">IP</label>
          <input
            type="text"
            value={ip}
            onChange={(e) => { setIp(e.target.value); setPage(1) }}
            placeholder="Dirección IP"
            className="mt-1 block w-36 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <button
          type="button"
          onClick={limpiarFiltros}
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Limpiar filtros
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  scope="col"
                  className={`px-4 py-3 text-left font-medium text-gray-700 cursor-pointer select-none hover:bg-gray-100`}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && sort === col.key && (
                      <span className="text-xs text-indigo-600">
                        {order === 'asc' ? '\u25B2' : '\u25BC'}
                      </span>
                    )}
                  </div>
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
            {!isLoading && logEntries.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-12 text-center text-sm text-gray-500">
                  No hay registros de auditoría.
                </td>
              </tr>
            )}
            {!isLoading &&
              logEntries.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 text-gray-700">
                    {new Date(entry.fecha).toLocaleString('es-AR')}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {entry.usuario_nombre ?? entry.usuario_id}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {entry.materia_nombre ?? entry.materia_id ?? '—'}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {entry.tipo_accion}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {entry.registros_afectados}
                  </td>
                  <td className="px-4 py-2.5 text-gray-700">
                    {entry.ip ?? '—'}
                  </td>
                  <td className="px-4 py-2.5 text-xs text-gray-500 max-w-xs truncate">
                    {entry.user_agent ?? '—'}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Mostrando página {page} de {totalPages} ({total} registros)
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              type="button"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
