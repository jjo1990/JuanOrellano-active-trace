import { useState, useCallback } from 'react'

interface ClonarEquipoProps {
  onClonar: (origen: string, destino: string) => void
  isLoading: boolean
}

export function ClonarEquipo({ onClonar, isLoading }: ClonarEquipoProps) {
  const [origen, setOrigen] = useState('')
  const [destino, setDestino] = useState('')
  const [confirmado, setConfirmado] = useState(false)

  const handleClonar = useCallback(() => {
    if (!confirmado || !origen || !destino) return
    onClonar(origen, destino)
    setConfirmado(false)
  }, [origen, destino, confirmado, onClonar])

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-6">
      <h3 className="text-lg font-medium text-gray-900">
        Clonar equipo entre períodos
      </h3>
      <p className="text-sm text-gray-500">
        Duplica todas las asignaciones vigentes de una cohorte a otra con nuevas fechas.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cohorte origen
          </label>
          <input
            type="text"
            value={origen}
            onChange={(e) => {
              setOrigen(e.target.value)
              setConfirmado(false)
            }}
            placeholder="ID cohorte origen..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cohorte destino
          </label>
          <input
            type="text"
            value={destino}
            onChange={(e) => {
              setDestino(e.target.value)
              setConfirmado(false)
            }}
            placeholder="ID cohorte destino..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="confirmar-clonado"
          checked={confirmado}
          onChange={(e) => setConfirmado(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <label
          htmlFor="confirmar-clonado"
          className="text-sm text-gray-600"
        >
          Confirmo que quiero duplicar todas las asignaciones
        </label>
      </div>

      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleClonar}
          disabled={
            isLoading || !origen || !destino || !confirmado
          }
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? 'Clonando...' : 'Clonar equipo'}
        </button>
      </div>
    </div>
  )
}
