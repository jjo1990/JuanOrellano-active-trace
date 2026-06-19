import { useState, useCallback } from 'react'
import type { Tarea, TareaEstado } from '@/features/coordinacion/types'

interface TareaWorkflowProps {
  tarea: Tarea
  onChangeEstado: (
    tareaId: string,
    estado: TareaEstado,
    comentario?: string
  ) => void
  onDelegar: (tareaId: string, nuevoAsignadoId: string) => void
  isLoading: boolean
}

const ESTADOS: TareaEstado[] = [
  'Pendiente',
  'En progreso',
  'Resuelta',
  'Cancelada',
]

const estadoVariant: Record<string, string> = {
  Pendiente: 'bg-yellow-100 text-yellow-800',
  'En progreso': 'bg-blue-100 text-blue-800',
  Resuelta: 'bg-green-100 text-green-800',
  Cancelada: 'bg-gray-100 text-gray-700',
}

export function TareaWorkflow({
  tarea,
  onChangeEstado,
  onDelegar,
  isLoading,
}: TareaWorkflowProps) {
  const [comentario, setComentario] = useState('')
  const [mostrarDelegar, setMostrarDelegar] = useState(false)
  const [nuevoAsignadoId, setNuevoAsignadoId] = useState('')

  const handleCambioEstado = useCallback(
    (estado: TareaEstado) => {
      onChangeEstado(tarea.id, estado, comentario || undefined)
      setComentario('')
    },
    [tarea.id, comentario, onChangeEstado]
  )

  const handleDelegar = useCallback(() => {
    if (!nuevoAsignadoId) return
    onDelegar(tarea.id, nuevoAsignadoId)
    setMostrarDelegar(false)
    setNuevoAsignadoId('')
  }, [tarea.id, nuevoAsignadoId, onDelegar])

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-900">
            {tarea.titulo}
          </h4>
          <p className="mt-0.5 text-xs text-gray-500">
            Asignado a: {tarea.asignado_a_nombre}
          </p>
        </div>
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            estadoVariant[tarea.estado] ?? 'bg-gray-100 text-gray-700'
          }`}
        >
          {tarea.estado}
        </span>
      </div>

      {tarea.descripcion && (
        <p className="text-sm text-gray-600">{tarea.descripcion}</p>
      )}

      <div className="flex flex-wrap items-center gap-2">
        {ESTADOS.map((estado) => {
          const esActual = tarea.estado === estado
          return (
            <button
              key={estado}
              type="button"
              disabled={esActual || isLoading}
              onClick={() => handleCambioEstado(estado)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                esActual
                  ? 'bg-indigo-100 text-indigo-700 cursor-default'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              } disabled:opacity-50`}
            >
              {estado}
            </button>
          )
        })}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          placeholder="Agregar comentario (opcional)..."
          className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-xs focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          type="button"
          onClick={() => setMostrarDelegar(!mostrarDelegar)}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
        >
          Delegar
        </button>
      </div>

      {mostrarDelegar && (
        <div className="flex gap-2">
          <input
            type="text"
            value={nuevoAsignadoId}
            onChange={(e) => setNuevoAsignadoId(e.target.value)}
            placeholder="ID nuevo docente..."
            className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-xs focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="button"
            onClick={handleDelegar}
            disabled={isLoading || !nuevoAsignadoId}
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            Confirmar
          </button>
        </div>
      )}
    </div>
  )
}
