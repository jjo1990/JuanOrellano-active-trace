import { useAvisoAcknowledgments } from '@/features/coordinacion/services/avisos'

interface AvisoAcknowledgmentsProps {
  avisoId: string
  onClose: () => void
}

export function AvisoAcknowledgments({
  avisoId,
  onClose,
}: AvisoAcknowledgmentsProps) {
  const { data, isLoading } = useAvisoAcknowledgments(avisoId)

  const confirmados = data ?? []
  const pendientes = 0

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">
            Confirmaciones de lectura
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
            <span className="ml-3 text-sm text-gray-500">Cargando...</span>
          </div>
        )}

        {!isLoading && (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-green-50 p-3 text-center">
                <p className="text-xs text-green-600">Confirmados</p>
                <p className="text-2xl font-bold text-green-700">
                  {confirmados.length}
                </p>
              </div>
              <div className="rounded-lg bg-yellow-50 p-3 text-center">
                <p className="text-xs text-yellow-600">Pendientes</p>
                <p className="text-2xl font-bold text-yellow-700">
                  {pendientes}
                </p>
              </div>
            </div>

            <div className="max-h-64 overflow-y-auto">
              {confirmados.length === 0 && (
                <p className="py-4 text-center text-sm text-gray-400">
                  Nadie confirmó aún.
                </p>
              )}
              {confirmados.map((ack) => (
                <div
                  key={ack.id}
                  className="flex items-center justify-between border-b border-gray-100 py-2 text-sm"
                >
                  <span className="text-gray-900">
                    {ack.usuario_nombre}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(ack.confirmado_en).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={onClose}
              className="w-full rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cerrar
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
