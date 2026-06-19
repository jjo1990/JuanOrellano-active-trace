import { useState, useCallback, useEffect } from 'react'
import { CohorteSelector } from '@/features/coordinacion/components/CohorteSelector'
import { DocentesAsignacion } from '@/features/coordinacion/components/DocentesAsignacion'
import { PadronImport } from '@/features/coordinacion/components/PadronImport'
import { FechasConfig } from '@/features/coordinacion/components/FechasConfig'
import { ConfirmacionResumen } from '@/features/coordinacion/components/ConfirmacionResumen'
import { useFechasAcademicas } from '@/features/coordinacion/services/programas'
import type {
  SetupPaso,
  SetupWizardState,
  AsignacionDocenteItem,
} from '@/features/coordinacion/types'

const STORAGE_KEY = 'setup-cuatrimestre-state'

const PASOS = [
  { key: 1 as SetupPaso, label: 'Cohorte' },
  { key: 2 as SetupPaso, label: 'Docentes' },
  { key: 3 as SetupPaso, label: 'Padrón' },
  { key: 4 as SetupPaso, label: 'Fechas' },
  { key: 5 as SetupPaso, label: 'Confirmar' },
]

function loadState(): SetupWizardState {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) return JSON.parse(stored) as SetupWizardState
  } catch {
    // ignore corrupt storage
  }
  return {
    paso_actual: 1,
    cohorte_id: '',
    cohorte_nombre: '',
    docentes_asignados: [],
    padron_importado: false,
    fechas_configuradas: [],
    completado: false,
  }
}

function saveState(state: SetupWizardState) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // ignore storage errors
  }
}

export function SetupCuatrimestre() {
  const [state, setState] = useState<SetupWizardState>(loadState)
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data: fechas } = useFechasAcademicas(
    state.cohorte_id || undefined
  )

  useEffect(() => {
    saveState(state)
  }, [state])

  useEffect(() => {
    if (fechas) {
      setState((prev) => ({ ...prev, fechas_configuradas: fechas }))
    }
  }, [fechas])

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleCohorteChange = useCallback(
    (id: string, nombre: string) => {
      setState((prev) => ({
        ...prev,
        cohorte_id: id,
        cohorte_nombre: nombre,
      }))
    },
    []
  )

  const handleDocentesAsignar = useCallback(
    (asignaciones: AsignacionDocenteItem[]) => {
      setState((prev) => ({ ...prev, docentes_asignados: asignaciones }))
    },
    []
  )

  const handleImportarPadron = useCallback(() => {
    setTimeout(() => {
      setState((prev) => ({ ...prev, padron_importado: true }))
      showMessage('Padrón importado.', 'success')
    }, 1500)
  }, [showMessage])

  const handleSiguiente = useCallback(() => {
    setState((prev) => ({
      ...prev,
      paso_actual: Math.min(prev.paso_actual + 1, 5) as SetupPaso,
    }))
  }, [])

  const handleAnterior = useCallback(() => {
    setState((prev) => ({
      ...prev,
      paso_actual: Math.max(prev.paso_actual - 1, 1) as SetupPaso,
    }))
  }, [])

  const handleIrAPaso = useCallback(
    (paso: SetupPaso) => {
      // Solo permite navegar a pasos ya completados o al actual+1
      if (paso <= state.paso_actual) {
        setState((prev) => ({ ...prev, paso_actual: paso }))
      }
    },
    [state.paso_actual]
  )

  const handleConfirmar = useCallback(() => {
    setState((prev) => ({ ...prev, completado: true }))
    showMessage('Setup completado.', 'success')
  }, [showMessage])

  const pasoActual = state.paso_actual

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Setup de cuatrimestre
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Configurá un nuevo período académico paso a paso
        </p>
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

      {state.completado && (
        <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">
            Setup completado exitosamente
          </p>
          <p className="mt-1 text-xs text-green-600">
            La cohorte {state.cohorte_nombre || state.cohorte_id} está lista.
          </p>
          <ConfirmacionResumen state={state} />
        </div>
      )}

      {/* Stepper */}
      <div className="mb-8">
        <nav aria-label="Progress">
          <ol className="flex items-center">
            {PASOS.map((paso, idx) => {
              const esCompletado = paso.key < pasoActual
              const esActual = paso.key === pasoActual
              const esPendiente = paso.key > pasoActual

              return (
                <li
                  key={paso.key}
                  className={`relative ${
                    idx < PASOS.length - 1 ? 'flex-1' : ''
                  }`}
                >
                  <div className="flex items-center">
                    <button
                      type="button"
                      onClick={() => handleIrAPaso(paso.key)}
                      disabled={esPendiente}
                      className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium transition-colors ${
                        esCompletado
                          ? 'bg-indigo-600 text-white cursor-pointer'
                          : esActual
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      {esCompletado ? '✓' : paso.key}
                    </button>
                    <span
                      className={`ml-2 text-xs font-medium ${
                        esCompletado || esActual
                          ? 'text-indigo-600'
                          : 'text-gray-400'
                      }`}
                    >
                      {paso.label}
                    </span>
                  </div>
                  {idx < PASOS.length - 1 && (
                    <div
                      className={`absolute left-8 top-4 h-0.5 w-full -translate-y-1/2 ${
                        esCompletado ? 'bg-indigo-600' : 'bg-gray-200'
                      }`}
                    />
                  )}
                </li>
              )
            })}
          </ol>
        </nav>
      </div>

      {/* Paso content */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        {pasoActual === 1 && (
          <CohorteSelector
            cohorteId={state.cohorte_id}
            cohorteNombre={state.cohorte_nombre}
            onChange={handleCohorteChange}
          />
        )}

        {pasoActual === 2 && (
          <DocentesAsignacion
            cohorteId={state.cohorte_id}
            asignados={state.docentes_asignados}
            onAsignar={handleDocentesAsignar}
          />
        )}

        {pasoActual === 3 && (
          <PadronImport
            importado={state.padron_importado}
            onImportar={handleImportarPadron}
            isLoading={false}
          />
        )}

        {pasoActual === 4 && (
          <FechasConfig
            fechas={state.fechas_configuradas}
            cohorteId={state.cohorte_id}
          />
        )}

        {pasoActual === 5 && <ConfirmacionResumen state={state} />}

        {/* Navigation */}
        <div className="mt-8 flex justify-between">
          <button
            type="button"
            onClick={handleAnterior}
            disabled={pasoActual === 1}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Anterior
          </button>

          {pasoActual < 5 ? (
            <button
              type="button"
              onClick={handleSiguiente}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Siguiente
            </button>
          ) : (
            <button
              type="button"
              onClick={handleConfirmar}
              disabled={state.completado}
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {state.completado ? 'Completado' : 'Confirmar setup'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
