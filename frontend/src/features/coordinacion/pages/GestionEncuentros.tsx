import { useState, useCallback } from 'react'
import { EncuentroForm } from '@/features/coordinacion/components/EncuentroForm'
import { CalendarioEncuentros } from '@/features/coordinacion/components/CalendarioEncuentros'
import { InstanciaEditor } from '@/features/coordinacion/components/InstanciaEditor'
import { GuardiasTable } from '@/features/coordinacion/components/GuardiasTable'
import {
  useEncuentros,
  useCreateEncuentro,
  useInstanciasEncuentro,
  useUpdateInstancia,
} from '@/features/coordinacion/services/encuentros'
import type {
  EncuentroFormValues,
  InstanciaEncuentro,
} from '@/features/coordinacion/types'

type Tab = 'calendario' | 'guardias'

const tabs: { key: Tab; label: string }[] = [
  { key: 'calendario', label: 'Calendario' },
  { key: 'guardias', label: 'Guardias' },
]

export function GestionEncuentros() {
  const [activeTab, setActiveTab] = useState<Tab>('calendario')
  const [showForm, setShowForm] = useState(false)
  const [cohorteId, setCohorteId] = useState('')
  const [selectedEncuentro, setSelectedEncuentro] = useState<string | null>(null)
  const [selectedInstancia, setSelectedInstancia] =
    useState<InstanciaEncuentro | null>(null)
  const [guardiaFilters, setGuardiaFilters] = useState<
    Record<string, string>
  >({})
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data: encuentros, isLoading: encIsLoading } =
    useEncuentros(cohorteId || undefined)
  const createMutation = useCreateEncuentro()
  const { data: instancias, isLoading: instIsLoading } =
    useInstanciasEncuentro(selectedEncuentro ?? '')
  const updateInstanciaMutation = useUpdateInstancia()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleCreate = useCallback(
    (data: EncuentroFormValues) => {
      createMutation.mutate(data, {
        onSuccess: (result) => {
          showMessage('Encuentro creado.', 'success')
          setShowForm(false)
          setSelectedEncuentro(result.id)
        },
        onError: () =>
          showMessage('Error al crear encuentro.', 'error'),
      })
    },
    [createMutation, showMessage]
  )

  const handleUpdateInstancia = useCallback(
    (
      id: string,
      data: {
        estado?: string
        meet_url?: string
        video_url?: string
        comentario?: string
      }
    ) => {
      updateInstanciaMutation.mutate(
        { id, data },
        {
          onSuccess: () => {
            showMessage('Instancia actualizada.', 'success')
            setSelectedInstancia(null)
          },
          onError: () =>
            showMessage('Error al actualizar instancia.', 'error'),
        }
      )
    },
    [updateInstanciaMutation, showMessage]
  )

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestión de encuentros
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Administrá los encuentros del cuatrimestre
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowForm(true)}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            + Nuevo encuentro
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

      {showForm && (
        <div className="mb-6">
          <EncuentroForm
            onSubmit={handleCreate}
            isLoading={createMutation.isPending}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      <div className="mb-4">
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-500">
              Cohorte
            </label>
            <input
              type="text"
              value={cohorteId}
              onChange={(e) => {
                setCohorteId(e.target.value)
                setSelectedEncuentro(null)
              }}
              placeholder="ID cohorte..."
              className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          {encuentros && encuentros.length > 0 && (
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Encuentro
              </label>
              <select
                value={selectedEncuentro ?? ''}
                onChange={(e) =>
                  setSelectedEncuentro(e.target.value || null)
                }
                className="mt-1 block w-60 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="">Seleccionar...</option>
                {encuentros.map((enc) => (
                  <option key={enc.id} value={enc.id}>
                    {enc.dia} {enc.hora_inicio} — {enc.materia_nombre ?? enc.materia_id}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
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
          {activeTab === 'calendario' && (
            <CalendarioEncuentros
              instancias={instancias ?? []}
              isLoading={instIsLoading}
              onSelectInstancia={setSelectedInstancia}
            />
          )}

          {activeTab === 'guardias' && (
            <div className="space-y-4">
              <div className="flex gap-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500">
                    Fecha
                  </label>
                  <input
                    type="date"
                    value={guardiaFilters.fecha ?? ''}
                    onChange={(e) =>
                      setGuardiaFilters({
                        ...guardiaFilters,
                        fecha: e.target.value || undefined,
                      })
                    }
                    className="mt-1 block rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <GuardiasTable filters={guardiaFilters} />
            </div>
          )}
        </div>
      </div>

      {selectedInstancia && (
        <InstanciaEditor
          instancia={selectedInstancia}
          onSave={handleUpdateInstancia}
          isLoading={updateInstanciaMutation.isPending}
          onClose={() => setSelectedInstancia(null)}
        />
      )}
    </div>
  )
}
