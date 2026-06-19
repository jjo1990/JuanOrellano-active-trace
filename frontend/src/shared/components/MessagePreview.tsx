import type {
  MessagePreview as MessagePreviewData,
} from '@/features/academico/types'

interface MessagePreviewProps {
  data: MessagePreviewData
  isLoading?: boolean
}

export function MessagePreview({
  data,
  isLoading = false,
}: MessagePreviewProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        <span className="ml-3 text-sm text-gray-500">
          Generando preview...
        </span>
      </div>
    )
  }

  if (!data) {
    return null
  }

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="text-sm font-medium text-gray-700">Asunto</h3>
        <p className="mt-1 text-sm text-gray-900">{data.asunto}</p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="text-sm font-medium text-gray-700">Cuerpo del mensaje</h3>
        <div
          className="mt-2 whitespace-pre-wrap text-sm text-gray-900"
          dangerouslySetInnerHTML={{ __html: data.cuerpo }}
        />
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-700">Destinatarios</h3>
          <span className="text-xs text-gray-500">
            {data.cantidad} destinatario{data.cantidad !== 1 ? 's' : ''}
          </span>
        </div>

        {data.destinatarios.length > 0 && (
          <ul className="mt-2 max-h-40 space-y-1 overflow-y-auto">
            {data.destinatarios.map((dest) => (
              <li
                key={dest.id}
                className="text-sm text-gray-700"
              >
                {dest.nombre} {dest.apellido} ({dest.email})
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
