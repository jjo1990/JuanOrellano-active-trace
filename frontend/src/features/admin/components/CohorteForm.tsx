import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { cohorteSchema, type CohorteFormValues, type Cohorte } from '@/features/admin/types'

interface CohorteFormProps {
  initialValues?: Cohorte
  onSubmit: (data: CohorteFormValues) => void
  onCancel: () => void
  isLoading: boolean
}

export function CohorteForm({
  initialValues,
  onSubmit,
  onCancel,
  isLoading,
}: CohorteFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<CohorteFormValues>({
    resolver: zodResolver(cohorteSchema),
    defaultValues: initialValues
      ? {
          nombre: initialValues.nombre,
          anio_inicio: initialValues.anio_inicio,
          vigencia_desde: initialValues.vigencia_desde?.split('T')[0] ?? '',
          vigencia_hasta: initialValues.vigencia_hasta?.split('T')[0] ?? '',
        }
      : {
          nombre: '',
          anio_inicio: new Date().getFullYear(),
          vigencia_desde: '',
          vigencia_hasta: '',
        },
  })

  const vigenciaDesde = watch('vigencia_desde')
  const vigenciaHasta = watch('vigencia_hasta')

  const hasVigenciaError =
    vigenciaDesde && vigenciaHasta && vigenciaDesde >= vigenciaHasta

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-gray-900">
        {initialValues ? 'Editar cohorte' : 'Nueva cohorte'}
      </h3>
      <div>
        <label className="block text-xs font-medium text-gray-500">Nombre</label>
        <input
          type="text"
          {...register('nombre')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.nombre && (
          <p className="mt-1 text-xs text-red-600">{errors.nombre.message}</p>
        )}
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-500">
          Año inicio
        </label>
        <input
          type="number"
          {...register('anio_inicio', { valueAsNumber: true })}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.anio_inicio && (
          <p className="mt-1 text-xs text-red-600">
            {errors.anio_inicio.message}
          </p>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Vigencia desde
          </label>
          <input
            type="date"
            {...register('vigencia_desde')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.vigencia_desde && (
            <p className="mt-1 text-xs text-red-600">
              {errors.vigencia_desde.message}
            </p>
          )}
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">
            Vigencia hasta
          </label>
          <input
            type="date"
            {...register('vigencia_hasta')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {hasVigenciaError && (
            <p className="mt-1 text-xs text-red-600">
              La fecha desde debe ser anterior a la fecha hasta
            </p>
          )}
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading || !!hasVigenciaError}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </form>
  )
}
