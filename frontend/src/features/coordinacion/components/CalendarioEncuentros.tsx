import { useState, useMemo } from 'react'
import type { InstanciaEncuentro } from '@/features/coordinacion/types'

interface CalendarioEncuentrosProps {
  instancias: InstanciaEncuentro[]
  isLoading: boolean
  onSelectInstancia: (instancia: InstanciaEncuentro) => void
}

const MESES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

const DIAS_SEMANA = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

export function CalendarioEncuentros({
  instancias,
  isLoading,
  onSelectInstancia,
}: CalendarioEncuentrosProps) {
  const ahora = new Date()
  const [year, setYear] = useState(ahora.getFullYear())
  const [month, setMonth] = useState(ahora.getMonth())

  const instanciasPorFecha = useMemo(() => {
    const map = new Map<string, InstanciaEncuentro[]>()
    for (const i of instancias) {
      const fechaKey = i.fecha.slice(0, 10)
      const existing = map.get(fechaKey) ?? []
      existing.push(i)
      map.set(fechaKey, existing)
    }
    return map
  }, [instancias])

  const primerDia = new Date(year, month, 1).getDay()
  const diasEnMes = new Date(year, month + 1, 0).getDate()

  const cambiarMes = (delta: number) => {
    const nuevoMes = month + delta
    if (nuevoMes < 0) {
      setMonth(11)
      setYear(year - 1)
    } else if (nuevoMes > 11) {
      setMonth(0)
      setYear(year + 1)
    } else {
      setMonth(nuevoMes)
    }
  }

  const celdas: (number | null)[] = []
  for (let i = 0; i < primerDia; i++) {
    celdas.push(null)
  }
  for (let d = 1; d <= diasEnMes; d++) {
    celdas.push(d)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        <span className="ml-3 text-sm text-gray-500">Cargando calendario...</span>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <button
          type="button"
          onClick={() => cambiarMes(-1)}
          className="rounded-md p-1 text-gray-500 hover:bg-gray-100"
        >
          ←
        </button>
        <span className="text-sm font-medium text-gray-900">
          {MESES[month]} {year}
        </span>
        <button
          type="button"
          onClick={() => cambiarMes(1)}
          className="rounded-md p-1 text-gray-500 hover:bg-gray-100"
        >
          →
        </button>
      </div>

      <div className="grid grid-cols-7 gap-px bg-gray-200">
        {DIAS_SEMANA.map((dia) => (
          <div
            key={dia}
            className="bg-gray-50 px-2 py-1 text-center text-xs font-medium text-gray-500"
          >
            {dia}
          </div>
        ))}

        {celdas.map((dia, idx) => {
          if (dia === null) {
            return (
              <div key={`empty-${idx}`} className="bg-white p-2 min-h-[4rem]" />
            )
          }

          const fechaStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`
          const instanciasDia = instanciasPorFecha.get(fechaStr) ?? []

          return (
            <div
              key={fechaStr}
              className="bg-white p-1.5 min-h-[4rem]"
            >
              <span className="text-xs text-gray-500">{dia}</span>
              {instanciasDia.length > 0 && (
                <div className="mt-0.5 space-y-0.5">
                  {instanciasDia.map((inst) => (
                    <button
                      key={inst.id}
                      type="button"
                      onClick={() => onSelectInstancia(inst)}
                      className={`block w-full truncate rounded px-1 py-0.5 text-left text-[10px] font-medium ${
                        inst.estado === 'Realizada'
                          ? 'bg-green-100 text-green-700'
                          : inst.estado === 'Cancelada'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-indigo-100 text-indigo-700'
                      }`}
                    >
                      {inst.encuentro_id.slice(0, 6)}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
