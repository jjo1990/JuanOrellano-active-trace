import { useState, useCallback } from 'react'
import { EquiposTable } from '@/features/coordinacion/components/EquiposTable'
import { AsignacionMasiva } from '@/features/coordinacion/components/AsignacionMasiva'
import { ClonarEquipo } from '@/features/coordinacion/components/ClonarEquipo'
import {
  useEquipos,
  useAsignarDocentes,
  useClonarEquipo,
  useUpdateVigencia,
  useExportEquipos,
} from '@/features/coordinacion/services/equipos'
import type {
  EquipoFilters,
  EquipoEntry,
} from '@/features/coordinacion/types'

type Tab = 'mis-equipos' | 'asignar' | 'historial'

const tabs: { key: Tab; label: string }[] = [
  { key: 'mis-equipos', label: 'Mis Equipos' },
  { key: 'asignar', label: 'Asignar' },
  { key: 'historial', label: 'Historial' },
]

export function GestionEquipos() {
  const [activeTab, setActiveTab] = useState<Tab>('mis-equipos')
  const [filters, setFilters] = useState<EquipoFilters>({})
  const [showVigenciaModal, setShowVigenciaModal] = useState(false)
  const [selectedEntry, setSelectedEntry] = useState<EquipoEntry | null>(null)
  const [nuevaFechaFin, setNuevaFechaFin] = useState('')
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data, isLoading } = useEquipos(filters)
  const asignarMutation = useAsignarDocentes()
  const clonarMutation = useClonarEquipo()
  const vigenciaMutation = useUpdateVigencia()
  const exportMutation = useExportEquipos()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleAsignar = useCallback(
    (
      asignaciones: {
        docente_id: string
        rol: string
        materia_id: string
        fecha_inicio: string
      }[]
    ) => {
      asignarMutation.mutate(
        { cohorte_id: '', asignaciones },
        {
          onSuccess: (result) => {
            showMessage(
              `${result.asignaciones_creadas} asignaciones creadas.`,
              'success'
            )
          },
          onError: () => showMessage('Error al asignar docentes.', 'error'),
        }
      )
    },
    [asignarMutation, showMessage]
  )

  const handleClonar = useCallback(
    (origen: string, destino: string) => {
      clonarMutation.mutate(
        {
          cohorte_origen_id: origen,
          cohorte_destino_id: destino,
        },
        {
          onSuccess: (result) => {
            showMessage(
              `${result.asignaciones_clonadas} asignaciones clonadas.`,
              'success'
            )
          },
          onError: () => showMessage('Error al clonar equipo.', 'error'),
        }
      )
    },
    [clonarMutation, showMessage]
  )

  const handleModificarVigencia = useCallback((entry: EquipoEntry) => {
    setSelectedEntry(entry)
    setNuevaFechaFin('')
    setShowVigenciaModal(true)
  }, [])

  const handleGuardarVigencia = useCallback(() => {
    if (!selectedEntry || !nuevaFechaFin) return
    vigenciaMutation.mutate(
      {
        asignacion_id: selectedEntry.id,
        fecha_fin: nuevaFechaFin,
      },
      {
        onSuccess: () => {
          showMessage('Vigencia actualizada.', 'success')
          setShowVigenciaModal(false)
          setSelectedEntry(null)
        },
        onError: () => showMessage('Error al actualizar vigencia.', 'error'),
      }
    )
  }, [selectedEntry, nuevaFechaFin, vigenciaMutation, showMessage])

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestión de equipos
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Asigná docentes a materias y gestioná los equipos del cuatrimestre
            </p>
          </div>
          <button
            type="button"
            onClick={() => exportMutation.mutate()}
            className="flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="1.5"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
              />
            </svg>
            Exportar
          </button>
        </div>
      </div>

      {message && (
        <div
          className={`mb-4 rounded-md px-4 py-3 text-sm ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-4 px-4" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4">
          {activeTab === 'mis-equipos' && (
            <div className="space-y-4">
              <div className="flex flex-wrap gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500">
                    Cohorte
                  </label>
                  <input
                    type="text"
                    value={filters.cohorte_id ?? ''}
                    onChange={(e) =>
                      setFilters({
                        ...filters,
                        cohorte_id: e.target.value || undefined,
                      })
                    }
                    placeholder="ID cohorte..."
                    className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500">
                    Materia
                  </label>
                  <input
                    type="text"
                    value={filters.materia_id ?? ''}
                    onChange={(e) =>
                      setFilters({
                        ...filters,
                        materia_id: e.target.value || undefined,
                      })
                    }
                    placeholder="ID materia..."
                    className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <EquiposTable
                data={data ?? []}
                isLoading={isLoading}
                onModificarVigencia={handleModificarVigencia}
              />
            </div>
          )}

          {activeTab === 'asignar' && (
            <AsignacionMasiva
              onAsignar={handleAsignar}
              isLoading={asignarMutation.isPending}
            />
          )}

          {activeTab === 'historial' && (
            <ClonarEquipo
              onClonar={handleClonar}
              isLoading={clonarMutation.isPending}
            />
          )}
        </div>
      </div>

      {showVigenciaModal && selectedEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl">
            <h3 className="text-lg font-medium text-gray-900">
              Modificar vigencia
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {selectedEntry.docente_nombre} — {selectedEntry.materia_nombre}
            </p>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">
                Nueva fecha fin
              </label>
              <input
                type="date"
                value={nuevaFechaFin}
                onChange={(e) => setNuevaFechaFin(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => {
                  setShowVigenciaModal(false)
                  setSelectedEntry(null)
                }}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleGuardarVigencia}
                disabled={vigenciaMutation.isPending || !nuevaFechaFin}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
