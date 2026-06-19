import type { ImportResult } from '@/features/academico/types'

interface ConfirmStepProps {
  selectedActividades: number
  totalActividades: number
  isImporting: boolean
  importResult?: ImportResult | null
  importError?: string | null
  onConfirm: () => void
  onBack: () => void
}

export function ConfirmStep({
  selectedActividades,
  totalActividades,
  isImporting,
  importResult,
  importError,
  onConfirm,
  onBack,
}: ConfirmStepProps) {
  if (importResult) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-green-200 bg-green-50 p-6 text-center">
          <svg
            className="mx-auto h-12 w-12 text-green-600"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="mt-3 text-lg font-semibold text-green-800">
            Importación completada
          </h2>
          <p className="mt-2 text-sm text-green-700">
            Se importaron {importResult.calificaciones_importadas}{' '}
            calificaciones de {importResult.alumnos_detectados} alumnos en{' '}
            {importResult.actividades_detectadas} actividades.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Paso 3: Confirmar importación
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Revisá los datos antes de confirmar la importación.
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <h3 className="text-sm font-medium text-gray-700">Resumen</h3>
        <dl className="mt-4 space-y-3">
          <div className="flex justify-between">
            <dt className="text-sm text-gray-500">Actividades seleccionadas</dt>
            <dd className="text-sm font-medium text-gray-900">
              {selectedActividades} de {totalActividades}
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-sm text-gray-500">Estado</dt>
            <dd className="text-sm font-medium text-gray-900">
              Listo para importar
            </dd>
          </div>
        </dl>
      </div>

      {selectedActividades === 0 && (
        <div className="rounded-md bg-yellow-50 p-3 text-sm text-yellow-700">
          Seleccioná al menos una actividad para importar.
        </div>
      )}

      {importError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          {importError}
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onBack}
          disabled={isImporting}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Volver
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={isImporting || selectedActividades === 0}
          className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {isImporting && (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          )}
          {isImporting ? 'Importando...' : 'Confirmar importación'}
        </button>
      </div>
    </div>
  )
}
