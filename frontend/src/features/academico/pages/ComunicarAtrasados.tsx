import { useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { SeleccionDestinatarios } from '@/features/academico/components/SeleccionDestinatarios'
import { TrackingEnvios } from '@/features/academico/components/TrackingEnvios'
import { HistorialComunicaciones } from '@/features/academico/components/HistorialComunicaciones'
import { MessagePreview } from '@/shared/components/MessagePreview'
import {
  usePreview,
  useEnviarComunicacion,
} from '@/features/academico/services/comunicaciones'
import type { MessagePreview as MessagePreviewData } from '@/features/academico/types'

type ComunicacionTab = 'destinatarios' | 'tracking' | 'historial'

const tabs: { key: ComunicacionTab; label: string }[] = [
  { key: 'destinatarios', label: 'Previsualizar y enviar' },
  { key: 'tracking', label: 'Tracking' },
  { key: 'historial', label: 'Historial' },
]

export function ComunicarAtrasados() {
  const { id: materiaId } = useParams<{ id: string }>()
  const [selected, setSelected] = useState<string[]>([])
  const [previewData, setPreviewData] = useState<MessagePreviewData | null>(null)
  const [loteId, setLoteId] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<ComunicacionTab>('destinatarios')
  const [error, setError] = useState<string | null>(null)

  const previewMutation = usePreview()
  const enviarMutation = useEnviarComunicacion()

  const handleToggle = useCallback((id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((a) => a !== id) : [...prev, id]
    )
    setPreviewData(null)
    setError(null)
  }, [])

  const handleSelectAll = useCallback(() => {
    setSelected([])
    setError(null)
  }, [])

  const handleDeselectAll = useCallback(() => {
    setSelected([])
    setPreviewData(null)
    setError(null)
  }, [])

  const handlePreview = useCallback(() => {
    if (!materiaId || selected.length === 0) {
      setError('Seleccioná al menos un destinatario')
      return
    }

    setError(null)
    previewMutation.mutate(
      { materiaId, destinatarios: selected },
      {
        onSuccess: (data) => setPreviewData(data),
      }
    )
  }, [materiaId, selected, previewMutation])

  const handleSend = useCallback(() => {
    if (!materiaId || selected.length === 0) return

    enviarMutation.mutate(
      {
        materia_id: materiaId,
        plantilla_id: 'default',
        destinatarios: selected,
      },
      {
        onSuccess: (result) => {
          setLoteId(result.lote_id)
          setActiveTab('tracking')
        },
      }
    )
  }, [materiaId, selected, enviarMutation])

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Comunicar atrasados
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Enviá comunicaciones a los alumnos con actividades pendientes
        </p>
      </div>

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
          {activeTab === 'destinatarios' && (
            <div className="space-y-6">
              <div>
                <h3 className="mb-3 text-sm font-medium text-gray-700">
                  1. Seleccioná los destinatarios
                </h3>
                <SeleccionDestinatarios
                  materiaId={materiaId ?? ''}
                  selected={selected}
                  onToggle={handleToggle}
                  onSelectAll={handleSelectAll}
                  onDeselectAll={handleDeselectAll}
                />
              </div>

              <div className="border-t border-gray-100 pt-6">
                <h3 className="mb-3 text-sm font-medium text-gray-700">
                  2. Previsualizá el mensaje
                </h3>

                {error && (
                  <div className="mb-3 rounded-md bg-yellow-50 p-3 text-sm text-yellow-700">
                    {error}
                  </div>
                )}

                <div className="mb-3">
                  <button
                    type="button"
                    onClick={handlePreview}
                    disabled={
                      selected.length === 0 || previewMutation.isPending
                    }
                    className="flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    {previewMutation.isPending && (
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
                    )}
                    {previewMutation.isPending
                      ? 'Generando...'
                      : 'Previsualizar mensaje'}
                  </button>
                </div>

                <MessagePreview
                  data={previewData!}
                  isLoading={previewMutation.isPending}
                />

                {previewData && (
                  <div className="mt-4">
                    <button
                      type="button"
                      onClick={handleSend}
                      disabled={enviarMutation.isPending}
                      className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                    >
                      {enviarMutation.isPending && (
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      )}
                      {enviarMutation.isPending
                        ? 'Enviando...'
                        : `Enviar a ${selected.length} destinatario${selected.length !== 1 ? 's' : ''}`}
                    </button>
                  </div>
                )}

                {enviarMutation.error && (
                  <div className="mt-3 rounded-md bg-red-50 p-3 text-sm text-red-700">
                    {(enviarMutation.error as Error).message}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'tracking' && (
            <div>
              <h3 className="mb-3 text-sm font-medium text-gray-700">
                Estado del envío en tiempo real
              </h3>
              <TrackingEnvios loteId={loteId} />
            </div>
          )}

          {activeTab === 'historial' && (
            <div>
              <h3 className="mb-3 text-sm font-medium text-gray-700">
                Historial de comunicaciones
              </h3>
              <HistorialComunicaciones materiaId={materiaId ?? ''} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
