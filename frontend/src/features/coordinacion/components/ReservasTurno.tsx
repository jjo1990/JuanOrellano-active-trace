import { useState } from 'react'
import { useTurnosColoquio } from '@/features/coordinacion/services/coloquios'
import type { TurnoColoquio } from '@/features/coordinacion/types'

interface ReservasTurnoProps {
  coloquioId: string
}

export function ReservasTurno({ coloquioId }: ReservasTurnoProps) {
  const { data: turnos, isLoading } = useTurnosColoquio(coloquioId)
  const [turnoExpandido, setTurnoExpandido] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        <span className="ml-3 text-sm text-gray-500">Cargando turnos...</span>
      </div>
    )
  }

  if (!turnos || turnos.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-gray-400">
        No hay turnos para esta convocatoria.
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {turnos.map((turno) => (
        <div
          key={turno.id}
          className="rounded-lg border border-gray-200 bg-white"
        >
          <button
            type="button"
            onClick={() =>
              setTurnoExpandido(
                turnoExpandido === turno.id ? null : turno.id
              )
            }
            className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-gray-50"
          >
            <div>
              <span className="text-sm font-medium text-gray-900">
                {turno.fecha.slice(0, 10)} — {turno.hora}
              </span>
              <span className="ml-3 text-xs text-gray-500">
                {turno.ocupado}/{turno.cupo} ocupados
              </span>
            </div>
            <span className="text-xs text-gray-400">
              {turno.reservas.length} reservas
            </span>
          </button>

          {turnoExpandido === turno.id && (
            <div className="border-t border-gray-100 px-4 py-2">
              {turno.reservas.length === 0 && (
                <p className="text-xs text-gray-400">Sin reservas</p>
              )}
              {turno.reservas.map((reserva) => (
                <div
                  key={reserva.id}
                  className="flex items-center justify-between border-b border-gray-50 py-2 text-sm"
                >
                  <span className="text-gray-900">
                    {reserva.alumno_nombre}
                  </span>
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs ${
                      reserva.confirmada
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {reserva.confirmada ? 'Confirmada' : 'Pendiente'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
