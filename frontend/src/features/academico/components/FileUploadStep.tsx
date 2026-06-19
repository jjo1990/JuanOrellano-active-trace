import { useCallback, useState, type ChangeEvent } from 'react'

interface FileUploadStepProps {
  materiaId?: string
  onFileSelected: (file: File) => void
  isUploading: boolean
  uploadError?: string | null
}

const ACCEPTED_TYPES = [
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/csv',
  'application/vnd.ms-excel',
]

export function FileUploadStep({
  materiaId,
  onFileSelected,
  isUploading,
  uploadError,
}: FileUploadStepProps) {
  const [dragOver, setDragOver] = useState(false)
  const [fileError, setFileError] = useState<string | null>(null)

  const validateFile = useCallback((file: File): boolean => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext !== 'xlsx' && ext !== 'csv') {
      setFileError('Formato no soportado. Usá .xlsx o .csv')
      return false
    }
    setFileError(null)
    return true
  }, [])

  const handleFile = useCallback(
    (file: File) => {
      if (validateFile(file)) {
        onFileSelected(file)
      }
    },
    [validateFile, onFileSelected]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Paso 1: Seleccionar archivo
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Subí el archivo de calificaciones exportado del LMS (.xlsx o .csv)
        </p>
      </div>

      <div
        className={`relative rounded-lg border-2 border-dashed p-12 text-center transition-colors ${
          dragOver
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${isUploading ? 'pointer-events-none opacity-50' : ''}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".xlsx,.csv"
          onChange={handleChange}
          disabled={isUploading || !materiaId}
          className="absolute inset-0 cursor-pointer opacity-0"
          aria-label="Seleccionar archivo de calificaciones"
        />

        <div className="space-y-2">
          <svg
            className="mx-auto h-10 w-10 text-gray-400"
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
          <p className="text-sm text-gray-600">
            {isUploading
              ? 'Procesando archivo...'
              : 'Arrastrá el archivo acá o hacé clic para seleccionarlo'}
          </p>
          <p className="text-xs text-gray-400">Formatos aceptados: .xlsx, .csv</p>
        </div>
      </div>

      {(fileError ?? uploadError) && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          {fileError ?? uploadError}
        </div>
      )}

      {isUploading && (
        <div className="flex items-center justify-center gap-2 py-4">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
          <span className="text-sm text-gray-600">Procesando archivo...</span>
        </div>
      )}
    </div>
  )
}
