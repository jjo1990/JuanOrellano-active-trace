import { useState } from 'react'
import { useLiquidacionPeriodo, useCerrarLiquidacion } from '@/features/finanzas/services/liquidaciones'
import { LiquidacionKpiCards } from '@/features/finanzas/components/LiquidacionKpiCards'
import { LiquidacionTable } from '@/features/finanzas/components/LiquidacionTable'
import { CerrarLiquidacionModal } from '@/features/finanzas/components/CerrarLiquidacionModal'
import type { LiquidacionEntry } from '@/features/finanzas/types'

type Segmento = 'general' | 'nexo' | 'factura'

export function LiquidacionesPeriodo() {
  const [cohorteId, setCohorteId] = useState('')
  const [mes, setMes] = useState(new Date().getMonth() + 1)
  const [anio, setAnio] = useState(new Date().getFullYear())
  const [segmento, setSegmento] = useState<Segmento>('general')
  const [showCerrarModal, setShowCerrarModal] = useState(false)

  const { data, isLoading } = useLiquidacionPeriodo(
    cohorteId,
    mes,
    anio
  )
  const cerrarMutation = useCerrarLiquidacion()

  const filteredEntries: LiquidacionEntry[] = (data?.entradas ?? []).filter(
    (entry) => entry.segmento === segmento
  )

  const segmentos: { key: Segmento; label: string }[] = [
    { key: 'general', label: 'General' },
    { key: 'nexo', label: 'NEXO' },
    { key: 'factura', label: 'Factura' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Liquidaciones del período
        </h1>
        {data && !data.cerrada && (
          <button
            type="button"
            onClick={() => setShowCerrarModal(true)}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
          >
            Cerrar liquidación
          </button>
        )}
      </div>

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
            value={mes}
            onChange={(e) => setMes(Number(e.target.value))}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
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
            value={anio}
            onChange={(e) => setAnio(Number(e.target.value))}
            className="mt-1 block w-24 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <LiquidacionKpiCards
        totalSinFactura={data?.total_sin_factura ?? 0}
        totalConFactura={data?.total_con_factura ?? 0}
      />

      {data?.cerrada && (
        <div className="rounded-md bg-yellow-50 border border-yellow-200 p-3">
          <p className="text-sm text-yellow-800">
            Esta liquidación fue cerrada el{' '}
            {data.fecha_cierre
              ? new Date(data.fecha_cierre).toLocaleDateString('es-AR')
              : '—'}
            . No puede modificarse.
          </p>
        </div>
      )}

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-4">
          {segmentos.map((seg) => (
            <button
              key={seg.key}
              type="button"
              onClick={() => setSegmento(seg.key)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                segmento === seg.key
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {seg.label}
              {data && (
                <span className="ml-2 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                  {data.entradas.filter((e) => e.segmento === seg.key).length}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <LiquidacionTable entries={filteredEntries} isLoading={isLoading} />

      <CerrarLiquidacionModal
        isOpen={showCerrarModal}
        onClose={() => setShowCerrarModal(false)}
        onConfirm={() => {
          cerrarMutation.mutate(
            { cohorteId, mes, anio },
            {
              onSuccess: () => setShowCerrarModal(false),
            }
          )
        }}
        isLoading={cerrarMutation.isPending}
      />
    </div>
  )
}
