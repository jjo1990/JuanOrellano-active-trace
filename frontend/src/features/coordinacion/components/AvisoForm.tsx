import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { avisoSchema, type AvisoFormValues } from '@/features/coordinacion/types'

interface AvisoFormProps {
  initialValues?: Partial<AvisoFormValues>
  onSubmit: (data: AvisoFormValues) => void
  isLoading: boolean
  onCancel: () => void
}

export function AvisoForm({
  initialValues,
  onSubmit,
  isLoading,
  onCancel,
}: AvisoFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AvisoFormValues>({
    resolver: zodResolver(avisoSchema),
    defaultValues: {
      titulo: '',
      cuerpo: '',
      scope: 'Global',
      severidad: 'Media',
      fecha_inicio: new Date().toISOString().slice(0, 10),
      fecha_fin: '',
      requiere_ack: false,
      ...initialValues,
    },
  })

  const scope = watch('scope')

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-4 rounded-lg border border-gray-200 bg-white p-6"
    >
      <h3 className="text-lg font-medium text-gray-900">
        {initialValues ? 'Editar aviso' : 'Nuevo aviso'}
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
          Cuerpo
        </label>
        <textarea
          {...register('cuerpo')}
          rows={4}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.cuerpo && (
          <p className="mt-1 text-xs text-red-600">
            {errors.cuerpo.message}
          </p>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Scope
          </label>
          <select
            {...register('scope')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="Global">Global</option>
            <option value="PorMateria">Por Materia</option>
            <option value="PorCohorte">Por Cohorte</option>
            <option value="PorRol">Por Rol</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Severidad
          </label>
          <select
            {...register('severidad')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="Baja">Baja</option>
            <option value="Media">Media</option>
            <option value="Alta">Alta</option>
            <option value="Urgente">Urgente</option>
          </select>
        </div>
      </div>

      {scope === 'PorMateria' && (
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Materia ID
          </label>
          <input
            {...register('scope_materia_id')}
            type="text"
            placeholder="ID de materia..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      )}

      {scope === 'PorCohorte' && (
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cohorte ID
          </label>
          <input
            {...register('scope_cohorte_id')}
            type="text"
            placeholder="ID de cohorte..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      )}

      {scope === 'PorRol' && (
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Rol destino
          </label>
          <input
            {...register('scope_rol')}
            type="text"
            placeholder="PROFESOR, TUTOR..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Fecha inicio
          </label>
          <input
            {...register('fecha_inicio')}
            type="date"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.fecha_inicio && (
            <p className="mt-1 text-xs text-red-600">
              {errors.fecha_inicio.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Fecha fin
          </label>
          <input
            {...register('fecha_fin')}
            type="date"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.fecha_fin && (
            <p className="mt-1 text-xs text-red-600">
              {errors.fecha_fin.message}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          {...register('requiere_ack')}
          type="checkbox"
          id="requiere-ack"
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <label
          htmlFor="requiere-ack"
          className="text-sm text-gray-600"
        >
          Requiere confirmación de lectura
        </label>
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
