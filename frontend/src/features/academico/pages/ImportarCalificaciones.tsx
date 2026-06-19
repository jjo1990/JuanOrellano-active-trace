import { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { FileUploadStep } from '@/features/academico/components/FileUploadStep'
import { PreviewStep } from '@/features/academico/components/PreviewStep'
import { ConfirmStep } from '@/features/academico/components/ConfirmStep'
import {
  useUploadPreview,
  useConfirmImport,
} from '@/features/academico/services/calificaciones'
import type { ImportPreview, ImportResult } from '@/features/academico/types'

type WizardStep = 'upload' | 'preview' | 'confirm'

export function ImportarCalificaciones() {
  const { id: materiaId } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [step, setStep] = useState<WizardStep>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<ImportPreview | null>(null)
  const [selectedActividades, setSelectedActividades] = useState<string[]>([])
  const [validationError, setValidationError] = useState<string | null>(null)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)

  const uploadMutation = useUploadPreview()
  const confirmMutation = useConfirmImport()

  const handleFileSelected = useCallback(
    (file: File) => {
      if (!materiaId) return
      setSelectedFile(file)

      uploadMutation.mutate(
        { file, materiaId },
        {
          onSuccess: (data) => {
            setPreview(data)
            setSelectedActividades(data.actividades.map((a) => a.id))
            setStep('preview')
          },
        }
      )
    },
    [materiaId, uploadMutation]
  )

  const handleToggleActividad = useCallback((id: string) => {
    setSelectedActividades((prev) =>
      prev.includes(id)
        ? prev.filter((a) => a !== id)
        : [...prev, id]
    )
    setValidationError(null)
  }, [])

  const handleGoToConfirm = useCallback(() => {
    if (selectedActividades.length === 0) {
      setValidationError('Seleccioná al menos una actividad')
      return
    }
    setValidationError(null)
    setStep('confirm')
  }, [selectedActividades])

  const handleConfirm = useCallback(() => {
    if (!materiaId || selectedActividades.length === 0) return

    confirmMutation.mutate(
      { materiaId, actividadIds: selectedActividades },
      {
        onSuccess: (result) => {
          setImportResult(result)
        },
      }
    )
  }, [materiaId, selectedActividades, confirmMutation])

  const handleBackToUpload = useCallback(() => {
    setStep('upload')
    setPreview(null)
    setSelectedFile(null)
    setSelectedActividades([])
    setValidationError(null)
    setImportResult(null)
  }, [])

  const handleBackToPreview = useCallback(() => {
    setStep('preview')
    setImportResult(null)
  }, [])

  const handleGoToDashboard = useCallback(() => {
    navigate(`/materias/${materiaId}/dashboard`)
  }, [navigate, materiaId])

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Importar calificaciones
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Subí el archivo exportado del LMS para cargar las calificaciones
        </p>
      </div>

      <div className="mb-8">
        <div className="flex items-center gap-2">
          {(['upload', 'preview', 'confirm'] as const).map((s, i) => {
            const isActive = step === s
            const isDone =
              (s === 'upload' && (step === 'preview' || step === 'confirm')) ||
              (s === 'preview' && step === 'confirm')

            return (
              <div key={s} className="flex items-center gap-2">
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
                    isActive
                      ? 'bg-indigo-600 text-white'
                      : isDone
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {isDone ? '\u2713' : i + 1}
                </div>
                <span
                  className={`text-sm font-medium ${
                    isActive ? 'text-indigo-600' : 'text-gray-500'
                  }`}
                >
                  {s === 'upload'
                    ? 'Subir'
                    : s === 'preview'
                      ? 'Previsualizar'
                      : 'Confirmar'}
                </span>
                {i < 2 && <div className="mx-2 h-px w-8 bg-gray-300" />}
              </div>
            )
          })}
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        {step === 'upload' && (
          <FileUploadStep
            materiaId={materiaId}
            onFileSelected={handleFileSelected}
            isUploading={uploadMutation.isPending}
            uploadError={
              uploadMutation.error
                ? (uploadMutation.error as Error).message
                : null
            }
          />
        )}

        {step === 'preview' && preview && (
          <>
            <PreviewStep
              preview={preview}
              selectedActividades={selectedActividades}
              onToggleActividad={handleToggleActividad}
              validationError={validationError}
            />

            <div className="mt-6 flex gap-3 border-t border-gray-100 pt-4">
              <button
                type="button"
                onClick={handleBackToUpload}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Volver
              </button>
              <button
                type="button"
                onClick={handleGoToConfirm}
                disabled={selectedActividades.length === 0}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                Continuar con {selectedActividades.length} actividad
                {selectedActividades.length !== 1 ? 'es' : ''}
              </button>
            </div>
          </>
        )}

        {step === 'confirm' && (
          <ConfirmStep
            selectedActividades={selectedActividades.length}
            totalActividades={preview?.actividades.length ?? 0}
            isImporting={confirmMutation.isPending}
            importResult={importResult}
            importError={
              confirmMutation.error
                ? (confirmMutation.error as Error).message
                : null
            }
            onConfirm={handleConfirm}
            onBack={handleBackToPreview}
          />
        )}

        {importResult && (
          <div className="mt-6 border-t border-gray-100 pt-4">
            <button
              type="button"
              onClick={handleGoToDashboard}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Ir al dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
