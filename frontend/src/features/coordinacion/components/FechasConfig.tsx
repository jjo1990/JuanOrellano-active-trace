import type { FechaAcademica } from '@/features/coordinacion/types'

interface FechasConfigProps {
  fechas: FechaAcademica[]
  cohorteId: string
}

export function FechasConfig({ fechas, cohorteId }: FechasConfigProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">
        Paso 4: Definir fechas académicas
      </h3>
      <p className="text-sm text-gray-500">
        Configurá las fechas clave: parciales, TPs, coloquios y recuperatorios.
      </p>

      {fechas.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
          <p className="text-sm text-gray-500">
            No hay fechas configuradas. Usá la sección "Programas y fechas" para agregarlas.
          </p>
          <p className="mt-1 text-xs text-gray-400">
            Cohorte: {cohorteId || '—'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {fechas.map((f, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3"
            >
              <div>
                <span className="text-sm font-medium text-gray-900">
                  {f.tipo}
                  {f.numero != null ? ` #${f.numero}` : ''}
                </span>
                <span className="ml-2 text-xs text-gray-500">
                  {f.materia_nombre ?? f.materia_id}
                </span>
              </div>
              <span className="text-sm text-gray-600">
                {f.fecha.slice(0, 10)}
              </span>
            </div>
          ))}
          <p className="text-xs text-gray-400">
            {fechas.length} fecha(s) configurada(s)
          </p>
        </div>
      )}
    </div>
  )
}
