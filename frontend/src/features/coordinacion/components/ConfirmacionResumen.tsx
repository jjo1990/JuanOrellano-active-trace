import type { SetupWizardState } from '@/features/coordinacion/types'

interface ConfirmacionResumenProps {
  state: SetupWizardState
}

export function ConfirmacionResumen({ state }: ConfirmacionResumenProps) {
  const pasosCompletados = [
    state.cohorte_id ? 1 : 0,
    state.docentes_asignados.length > 0 ? 1 : 0,
    state.padron_importado ? 1 : 0,
    state.fechas_configuradas.length > 0 ? 1 : 0,
    1,
  ].filter(Boolean).length

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">
        Paso 5: Revisar y confirmar
      </h3>
      <p className="text-sm text-gray-500">
        Revisá el resumen de la configuración antes de confirmar.
      </p>

      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              Progreso total
            </span>
            <span className="text-sm font-bold text-indigo-600">
              {pasosCompletados}/5 completado
            </span>
          </div>
          <div className="mt-2 h-2 rounded-full bg-gray-100">
            <div
              className="h-2 rounded-full bg-indigo-600 transition-all"
              style={{
                width: `${(pasosCompletados / 5) * 100}%`,
              }}
            />
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-gray-100 py-2">
            <span className="text-sm text-gray-600">Cohorte</span>
            <span className="text-sm font-medium text-gray-900">
              {state.cohorte_nombre || state.cohorte_id || '—'}
            </span>
          </div>
          <div className="flex items-center justify-between border-b border-gray-100 py-2">
            <span className="text-sm text-gray-600">Docentes asignados</span>
            <span className="text-sm font-medium text-gray-900">
              {state.docentes_asignados.length}
            </span>
          </div>
          <div className="flex items-center justify-between border-b border-gray-100 py-2">
            <span className="text-sm text-gray-600">Padrón</span>
            <span
              className={`text-sm font-medium ${
                state.padron_importado
                  ? 'text-green-600'
                  : 'text-gray-400'
              }`}
            >
              {state.padron_importado ? 'Importado' : 'Pendiente'}
            </span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm text-gray-600">Fechas académicas</span>
            <span className="text-sm font-medium text-gray-900">
              {state.fechas_configuradas.length} configuradas
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
