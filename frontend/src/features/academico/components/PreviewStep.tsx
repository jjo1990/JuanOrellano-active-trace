import type { ImportPreview } from '@/features/academico/types'

interface PreviewStepProps {
  preview: ImportPreview
  selectedActividades: string[]
  onToggleActividad: (id: string) => void
  validationError?: string | null
}

export function PreviewStep({
  preview,
  selectedActividades,
  onToggleActividad,
  validationError,
}: PreviewStepProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Paso 2: Vista previa
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Se detectaron {preview.alumnos.length} alumnos y{' '}
          {preview.actividades.length} actividades. Seleccioná las actividades a
          importar.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-medium text-gray-700">
            Actividades detectadas
          </h3>

          {validationError && (
            <p className="mt-2 text-sm text-red-600">{validationError}</p>
          )}

          <div className="mt-3 space-y-2">
            {preview.actividades.map((act) => (
              <label
                key={act.id}
                className="flex cursor-pointer items-center gap-3 rounded-md border border-gray-200 p-3 hover:bg-gray-50"
              >
                <input
                  type="checkbox"
                  checked={selectedActividades.includes(act.id)}
                  onChange={() => onToggleActividad(act.id)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <div>
                  <span className="text-sm font-medium text-gray-900">
                    {act.nombre}
                  </span>
                  <span className="ml-2 text-xs text-gray-400">
                    {act.tipo}
                    {act.peso != null ? ` \u00B7 Peso: ${act.peso}` : ''}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-medium text-gray-700">
            Alumnos ({preview.alumnos.length})
          </h3>
          <ul className="mt-3 max-h-80 space-y-1 overflow-y-auto">
            {preview.alumnos.map((alumno) => (
              <li key={alumno.id} className="text-sm text-gray-700">
                {alumno.nombre} {alumno.apellido}{' '}
                <span className="text-xs text-gray-400">
                  ({alumno.legajo})
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="text-sm font-medium text-gray-700">
          Muestra de calificaciones
        </h3>
        {preview.calificaciones_preview.length === 0 ? (
          <p className="mt-2 text-sm text-gray-400">
            No hay calificaciones para mostrar en la vista previa.
          </p>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="pb-2 text-left font-medium text-gray-600">
                    Alumno
                  </th>
                  <th className="pb-2 text-left font-medium text-gray-600">
                    Actividad
                  </th>
                  <th className="pb-2 text-right font-medium text-gray-600">
                    Nota
                  </th>
                </tr>
              </thead>
              <tbody>
                {preview.calificaciones_preview.slice(0, 20).map((cal, i) => (
                  <tr key={`${cal.alumno_id}-${cal.actividad_id}-${i}`}>
                    <td className="py-1.5 text-gray-700">
                      {cal.alumno_nombre ?? cal.alumno_id}
                    </td>
                    <td className="py-1.5 text-gray-700">
                      {cal.actividad_nombre ?? cal.actividad_id}
                    </td>
                    <td className="py-1.5 text-right text-gray-700">
                      {cal.nota}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
