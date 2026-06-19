import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  useUmbral,
  useUpdateUmbral,
} from '@/features/academico/services/umbrales'
import {
  umbralSchema,
  type UmbralFormValues,
} from '@/features/academico/types'

export function ConfigurarUmbral() {
  const { id: materiaId } = useParams<{ id: string }>()
  const { data: umbral, isLoading } = useUmbral(materiaId ?? '')
  const updateMutation = useUpdateUmbral()

  const {
    control,
    handleSubmit,
    reset,
    formState: { isDirty },
  } = useForm<UmbralFormValues>({
    resolver: zodResolver(umbralSchema),
    defaultValues: { porcentaje: 60 },
  })

  useEffect(() => {
    if (umbral) {
      reset({ porcentaje: umbral.porcentaje })
    }
  }, [umbral, reset])

  const onSubmit = (data: UmbralFormValues) => {
    if (!materiaId) return
    updateMutation.mutate({ materiaId, porcentaje: data.porcentaje })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        <span className="ml-3 text-sm text-gray-500">Cargando umbral...</span>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Configurar umbral de aprobación
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Definí el porcentaje mínimo para considerar una actividad como
          aprobada. Valor por defecto: 60%.
        </p>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
      >
        <div className="space-y-4">
          <div>
            <label
              htmlFor="porcentaje"
              className="block text-sm font-medium text-gray-700"
            >
              Porcentaje de aprobación
            </label>

            <Controller
              name="porcentaje"
              control={control}
              render={({ field, fieldState: { error } }) => (
                <div className="mt-2">
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min={0}
                      max={100}
                      step={5}
                      value={field.value}
                      onChange={(e) => field.onChange(Number(e.target.value))}
                      className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-gray-200 accent-indigo-600"
                    />
                    <input
                      type="number"
                      id="porcentaje"
                      min={0}
                      max={100}
                      value={field.value}
                      onChange={(e) => {
                        const val = Number(e.target.value)
                        if (!isNaN(val)) field.onChange(val)
                      }}
                      className="w-20 rounded-md border border-gray-300 px-3 py-1.5 text-center text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                    <span className="text-sm font-medium text-gray-700">%</span>
                  </div>
                  {error && (
                    <p className="mt-1 text-sm text-red-600">{error.message}</p>
                  )}
                </div>
              )}
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={!isDirty || updateMutation.isPending}
              className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {updateMutation.isPending && (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              )}
              {updateMutation.isPending ? 'Guardando...' : 'Guardar umbral'}
            </button>

            {!isDirty && umbral && (
              <span className="text-sm text-gray-400">
                Umbral actual: {umbral.porcentaje}%
              </span>
            )}
          </div>

          {updateMutation.isSuccess && (
            <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
              Umbral actualizado a{' '}
              {updateMutation.variables?.porcentaje}%
            </div>
          )}

          {updateMutation.error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              {(updateMutation.error as Error).message}
            </div>
          )}
        </div>
      </form>
    </div>
  )
}
