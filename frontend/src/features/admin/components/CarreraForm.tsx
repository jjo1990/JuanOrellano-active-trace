import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { carreraSchema, type CarreraFormValues, type Carrera } from '@/features/admin/types'

interface CarreraFormProps {
  initialValues?: Carrera
  onSubmit: (data: CarreraFormValues) => void
  onCancel: () => void
  isLoading: boolean
}

export function CarreraForm({
  initialValues,
  onSubmit,
  onCancel,
  isLoading,
}: CarreraFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CarreraFormValues>({
    resolver: zodResolver(carreraSchema),
    defaultValues: initialValues
      ? {
          codigo: initialValues.codigo,
          nombre: initialValues.nombre,
        }
      : {
          codigo: '',
          nombre: '',
        },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-gray-900">
        {initialValues ? 'Editar carrera' : 'Nueva carrera'}
      </h3>
      <div>
        <label className="block text-xs font-medium text-gray-500">Código</label>
        <input
          type="text"
          {...register('codigo')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.codigo && (
          <p className="mt-1 text-xs text-red-600">{errors.codigo.message}</p>
        )}
      </div>
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
          disabled={isLoading}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </form>
  )
}
