import { useState } from 'react'
import { AuditoriaAccionesPorDia } from '@/features/admin/components/AuditoriaAccionesPorDia'
import { AuditoriaEstadoComunicaciones } from '@/features/admin/components/AuditoriaEstadoComunicaciones'
import { AuditoriaInteracciones } from '@/features/admin/components/AuditoriaInteracciones'
import { AuditoriaUltimasAcciones } from '@/features/admin/components/AuditoriaUltimasAcciones'
import type { AuditoriaFilters } from '@/features/admin/types'

type SubVista =
  | 'acciones-por-dia'
  | 'comunicaciones'
  | 'interacciones'
  | 'ultimas-acciones'

export function PanelAuditoria() {
  const [subVista, setSubVista] = useState<SubVista>('acciones-por-dia')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [usuarioId, setUsuarioId] = useState('')
  const [tipoAccion, setTipoAccion] = useState('')

  const filters: AuditoriaFilters = {
    ...(fechaDesde ? { fecha_desde: fechaDesde } : {}),
    ...(fechaHasta ? { fecha_hasta: fechaHasta } : {}),
    ...(materiaId ? { materia_id: materiaId } : {}),
    ...(usuarioId ? { usuario_id: usuarioId } : {}),
    ...(tipoAccion ? { tipo_accion: tipoAccion } : {}),
  }

  const subVistas: { key: SubVista; label: string }[] = [
    { key: 'acciones-por-dia', label: 'Acciones por día' },
    { key: 'comunicaciones', label: 'Comunicaciones' },
    { key: 'interacciones', label: 'Interacciones' },
    { key: 'ultimas-acciones', label: 'Últimas acciones' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Panel de auditoría</h1>

      <div className="flex flex-wrap gap-4 rounded-lg border border-gray-200 bg-white p-4">
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
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Materia
          </label>
          <input
            type="text"
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
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
            onChange={(e) => setUsuarioId(e.target.value)}
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
            onChange={(e) => setTipoAccion(e.target.value)}
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
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-4">
          {subVistas.map((sv) => (
            <button
              key={sv.key}
              type="button"
              onClick={() => setSubVista(sv.key)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                subVista === sv.key
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {sv.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        {subVista === 'acciones-por-dia' && (
          <AuditoriaAccionesPorDia filters={filters} />
        )}
        {subVista === 'comunicaciones' && (
          <AuditoriaEstadoComunicaciones filters={filters} />
        )}
        {subVista === 'interacciones' && (
          <AuditoriaInteracciones filters={filters} />
        )}
        {subVista === 'ultimas-acciones' && (
          <AuditoriaUltimasAcciones filters={filters} />
        )}
      </div>
    </div>
  )
}
