import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  convocatoriaSchema,
  type ConvocatoriaFormValues,
} from '@/features/coordinacion/types'

const DIAS_OPTIONS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

interface ConvocatoriaFormProps {
  onSubmit: (data: ConvocatoriaFormValues) => void
  isLoading: boolean
  onCancel: () => void
}

export function ConvocatoriaForm({
  onSubmit,
  isLoading,
  onCancel,
}: ConvocatoriaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ConvocatoriaFormValues>({
    resolver: zodResolver(convocatoriaSchema),
    defaultValues: {
      materia_id: '',
      cohorte_id: '',
      dias: [],
      cupo_por_turno: 5,
    },
  })

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-4 rounded-lg border border-gray-200 bg-white p-6"
    >
      <h3 className="text-lg font-medium text-gray-900">
        Nueva convocatoria
      </h3>

      <div className="grid gap-4 sm:grid-cols-2">
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

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Días disponibles
        </label>
        <DiasCheckboxGroup
          name="dias"
          register={register}
          errors={errors}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Cupo por turno
        </label>
        <input
          {...register('cupo_por_turno', { valueAsNumber: true })}
          type="number"
          min={1}
          max={20}
          className="mt-1 block w-32 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.cupo_por_turno && (
          <p className="mt-1 text-xs text-red-600">
            {errors.cupo_por_turno.message}
          </p>
        )}
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
          {isLoading ? 'Creando...' : 'Crear convocatoria'}
        </button>
      </div>
    </form>
  )
}

function DiasCheckboxGroup({
  name,
  register,
  errors,
}: {
  name: string
  register: ReturnType<typeof useForm>['register']
  errors: Record<string, { message?: string }>
}) {
  return (
    <div className="mt-1 flex flex-wrap gap-3">
      {DIAS_OPTIONS.map((dia) => (
        <label
          key={dia}
          className="flex items-center gap-2 rounded-md border border-gray-200 px-3 py-2 text-sm hover:bg-gray-50"
        >
          <input
            type="checkbox"
            value={dia}
            {...register(name)}
            className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          {dia}
        </label>
      ))}
      {errors[name] && (
        <p className="w-full text-xs text-red-600">
          {(errors[name] as unknown as { message: string }).message}
        </p>
      )}
    </div>
  )
}
