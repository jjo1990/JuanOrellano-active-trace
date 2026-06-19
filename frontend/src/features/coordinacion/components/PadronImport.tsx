interface PadronImportProps {
  importado: boolean
  onImportar: () => void
  isLoading: boolean
}

export function PadronImport({
  importado,
  onImportar,
  isLoading,
}: PadronImportProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">
        Paso 3: Importar padrón
      </h3>
      <p className="text-sm text-gray-500">
        Importá el padrón de alumnos desde Moodle para tener la lista actualizada.
      </p>

      {importado ? (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">
            Padrón importado correctamente
          </p>
          <p className="mt-1 text-xs text-green-600">
            Los alumnos ya están disponibles para las asignaciones.
          </p>
        </div>
      ) : (
        <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
          <svg
            className="mx-auto h-8 w-8 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-500">
            No se importó el padrón todavía
          </p>
          <button
            type="button"
            onClick={onImportar}
            disabled={isLoading}
            className="mt-3 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {isLoading ? 'Importando...' : 'Importar padrón'}
          </button>
        </div>
      )}
    </div>
  )
}
