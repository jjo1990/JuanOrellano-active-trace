import { useState, useCallback } from 'react'
import type { InstanciaEncuentro } from '@/features/coordinacion/types'

interface InstanciaEditorProps {
  instancia: InstanciaEncuentro
  onSave: (
    id: string,
    data: {
      estado?: string
      meet_url?: string
      video_url?: string
      comentario?: string
    }
  ) => void
  isLoading: boolean
  onClose: () => void
}

export function InstanciaEditor({
  instancia,
  onSave,
  isLoading,
  onClose,
}: InstanciaEditorProps) {
  const [estado, setEstado] = useState(instancia.estado)
  const [meetUrl, setMeetUrl] = useState(instancia.meet_url ?? '')
  const [videoUrl, setVideoUrl] = useState(instancia.video_url ?? '')
  const [comentario, setComentario] = useState(instancia.comentario ?? '')

  const handleSave = useCallback(() => {
    onSave(instancia.id, {
      estado,
      meet_url: meetUrl || undefined,
      video_url: videoUrl || undefined,
      comentario: comentario || undefined,
    })
  }, [instancia.id, estado, meetUrl, videoUrl, comentario, onSave])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Editar instancia
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>

        <p className="mt-1 text-sm text-gray-500">
          {instancia.fecha.slice(0, 10)}
        </p>

        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Estado
            </label>
            <select
              value={estado}
              onChange={(e) => setEstado(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="Programada">Programada</option>
              <option value="Realizada">Realizada</option>
              <option value="Cancelada">Cancelada</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Meet URL
            </label>
            <input
              type="url"
              value={meetUrl}
              onChange={(e) => setMeetUrl(e.target.value)}
              placeholder="https://meet.google.com/..."
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Video URL
            </label>
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="https://..."
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Comentario
            </label>
            <textarea
              value={comentario}
              onChange={(e) => setComentario(e.target.value)}
              rows={2}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={isLoading}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  )
}
