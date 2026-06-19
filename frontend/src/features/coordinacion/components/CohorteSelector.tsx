interface CohorteSelectorProps {
  cohorteId: string
  cohorteNombre: string
  onChange: (id: string, nombre: string) => void
}

export function CohorteSelector({
  cohorteId,
  cohorteNombre,
  onChange,
}: CohorteSelectorProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">
        Paso 1: Crear o seleccionar cohorte
      </h3>
      <p className="text-sm text-gray-500">
        La cohorte define el período académico. Podés crear una nueva o seleccionar una existente.
      </p>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            ID Cohorte
          </label>
          <input
            type="text"
            value={cohorteId}
            onChange={(e) => onChange(e.target.value, cohorteNombre)}
            placeholder="Ej: 2025-C1"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Nombre de cohorte
          </label>
          <input
            type="text"
            value={cohorteNombre}
            onChange={(e) => onChange(cohorteId, e.target.value)}
            placeholder="Ej: Primer cuatrimestre 2025"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>
    </div>
  )
}
