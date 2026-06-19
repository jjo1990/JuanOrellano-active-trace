import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { salarioBaseSchema, type SalarioBaseFormValues, type SalarioBase } from '@/features/finanzas/types'

interface SalarioBaseFormProps {
  initialValues?: SalarioBase
  onSubmit: (data: SalarioBaseFormValues) => void
  onCancel: () => void
  isLoading: boolean
}

export function SalarioBaseForm({
  initialValues,
  onSubmit,
  onCancel,
  isLoading,
}: SalarioBaseFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SalarioBaseFormValues>({
    resolver: zodResolver(salarioBaseSchema),
    defaultValues: initialValues
      ? {
          rol: initialValues.rol,
          monto: initialValues.monto,
          vigencia_desde: initialValues.vigencia_desde?.split('T')[0] ?? '',
          vigencia_hasta: initialValues.vigencia_hasta?.split('T')[0] ?? '',
        }
      : {
          rol: '',
          monto: 0,
          vigencia_desde: '',
          vigencia_hasta: '',
        },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-gray-900">
        {initialValues ? 'Editar salario base' : 'Nuevo salario base'}
      </h3>

      <div>
        <label className="block text-xs font-medium text-gray-500">Rol</label>
        <select
          {...register('rol')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">Seleccionar rol</option>
          <option value="PROFESOR">PROFESOR</option>
          <option value="TUTOR">TUTOR</option>
          <option value="COORDINADOR">COORDINADOR</option>
          <option value="NEXO">NEXO</option>
        </select>
        {errors.rol && (
          <p className="mt-1 text-xs text-red-600">{errors.rol.message}</p>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500">Monto</label>
        <input
          type="number"
          step="0.01"
          {...register('monto', { valueAsNumber: true })}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.monto && (
          <p className="mt-1 text-xs text-red-600">{errors.monto.message}</p>
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
          disabled={isLoading}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </form>
  )
}
