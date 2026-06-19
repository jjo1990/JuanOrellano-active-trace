import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  encuentroSchema,
  type EncuentroFormValues,
} from '@/features/coordinacion/types'

interface EncuentroFormProps {
  onSubmit: (data: EncuentroFormValues) => void
  isLoading: boolean
  onCancel: () => void
}

export function EncuentroForm({
  onSubmit,
  isLoading,
  onCancel,
}: EncuentroFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<EncuentroFormValues>({
    resolver: zodResolver(encuentroSchema),
    defaultValues: {
      dia: 'Lunes',
      hora_inicio: '09:00',
      hora_fin: '11:00',
      meet_url: '',
      tipo: 'Recurrente',
      cantidad_semanas: 16,
      materia_id: '',
      docente_id: '',
      cohorte_id: '',
    },
  })

  const tipo = watch('tipo')

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-4 rounded-lg border border-gray-200 bg-white p-6"
    >
      <h3 className="text-lg font-medium text-gray-900">
        Nuevo encuentro
      </h3>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Tipo
        </label>
        <select
          {...register('tipo')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="Recurrente">Recurrente</option>
          <option value="Unico">Único</option>
        </select>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Día
          </label>
          <select
            {...register('dia')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="Lunes">Lunes</option>
            <option value="Martes">Martes</option>
            <option value="Miércoles">Miércoles</option>
            <option value="Jueves">Jueves</option>
            <option value="Viernes">Viernes</option>
            <option value="Sábado">Sábado</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Hora inicio
          </label>
          <input
            {...register('hora_inicio')}
            type="time"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.hora_inicio && (
            <p className="mt-1 text-xs text-red-600">
              {errors.hora_inicio.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Hora fin
          </label>
          <input
            {...register('hora_fin')}
            type="time"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.hora_fin && (
            <p className="mt-1 text-xs text-red-600">
              {errors.hora_fin.message}
            </p>
          )}
        </div>

        {tipo === 'Recurrente' && (
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Cantidad de semanas
            </label>
            <input
              {...register('cantidad_semanas', { valueAsNumber: true })}
              type="number"
              min={1}
              max={52}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Meet URL
        </label>
        <input
          {...register('meet_url')}
          type="url"
          placeholder="https://meet.google.com/..."
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Materia ID
          </label>
          <input
            {...register('materia_id')}
            type="text"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.materia_id && (
            <p className="mt-1 text-xs text-red-600">
              {errors.materia_id.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Docente ID
          </label>
          <input
            {...register('docente_id')}
            type="text"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.docente_id && (
            <p className="mt-1 text-xs text-red-600">
              {errors.docente_id.message}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Cohorte ID
          </label>
          <input
            {...register('cohorte_id')}
            type="text"
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.cohorte_id && (
            <p className="mt-1 text-xs text-red-600">
              {errors.cohorte_id.message}
            </p>
          )}
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
          {isLoading ? 'Creando...' : 'Crear encuentro'}
        </button>
      </div>
    </form>
  )
}
