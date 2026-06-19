import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { tareaSchema, type TareaFormValues } from '@/features/coordinacion/types'

interface TareaFormProps {
  initialValues?: Partial<TareaFormValues>
  onSubmit: (data: TareaFormValues) => void
  isLoading: boolean
  onCancel: () => void
}

export function TareaForm({
  initialValues,
  onSubmit,
  isLoading,
  onCancel,
}: TareaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TareaFormValues>({
    resolver: zodResolver(tareaSchema),
    defaultValues: {
      titulo: '',
      descripcion: '',
      asignado_a_id: '',
      materia_id: '',
      fecha_limite: '',
      ...initialValues,
    },
  })

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-4 rounded-lg border border-gray-200 bg-white p-6"
    >
      <h3 className="text-lg font-medium text-gray-900">
        {initialValues?.titulo ? 'Editar tarea' : 'Nueva tarea'}
      </h3>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Título
        </label>
        <input
          {...register('titulo')}
          type="text"
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.titulo && (
          <p className="mt-1 text-xs text-red-600">
            {errors.titulo.message}
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Descripción
        </label>
        <textarea
          {...register('descripcion')}
          rows={3}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Asignado a (ID)
          </label>
          <input
            {...register('asignado_a_id')}
            type="text"
            placeholder="ID de docente..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.asignado_a_id && (
            <p className="mt-1 text-xs text-red-600">
              {errors.asignado_a_id.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Materia (opcional)
          </label>
          <input
            {...register('materia_id')}
            type="text"
            placeholder="ID de materia..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Fecha límite
          </label>
          <input
            {...register('fecha_limite')}
            type="date"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </form>
  )
}
