import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { usuarioSchema, type UsuarioFormValues, type UsuarioTenant } from '@/features/admin/types'

interface UsuarioFormProps {
  initialValues?: UsuarioTenant
  onSubmit: (data: UsuarioFormValues) => void
  onCancel: () => void
  isLoading: boolean
}

const ROLES_DISPONIBLES = ['PROFESOR', 'TUTOR', 'COORDINADOR', 'NEXO', 'FINANZAS', 'ADMIN']

export function UsuarioForm({
  initialValues,
  onSubmit,
  onCancel,
  isLoading,
}: UsuarioFormProps) {
  const [selectedRoles, setSelectedRoles] = useState<string[]>(
    initialValues?.roles ?? []
  )

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UsuarioFormValues>({
    resolver: zodResolver(usuarioSchema),
    defaultValues: initialValues
      ? {
          nombre: initialValues.nombre,
          email: initialValues.email,
          identificacion_fiscal: initialValues.identificacion_fiscal ?? '',
          roles: initialValues.roles,
          banco: initialValues.banco ?? '',
          cbu: initialValues.cbu ?? '',
          alias_cbu: initialValues.alias_cbu ?? '',
          regional: initialValues.regional ?? '',
          modalidad_facturacion: initialValues.modalidad_facturacion ?? '',
        }
      : {
          nombre: '',
          email: '',
          identificacion_fiscal: '',
          roles: [],
          banco: '',
          cbu: '',
          alias_cbu: '',
          regional: '',
          modalidad_facturacion: '',
        },
  })

  const handleRoleToggle = (role: string) => {
    setSelectedRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]
    )
  }

  const handleFormSubmit = (data: UsuarioFormValues) => {
    onSubmit({ ...data, roles: selectedRoles })
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-gray-900">
        {initialValues ? 'Editar usuario' : 'Nuevo usuario'}
      </h3>

      <div className="grid grid-cols-2 gap-4">
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
          <label className="block text-xs font-medium text-gray-500">Email</label>
          <input
            type="email"
            {...register('email')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {errors.email && (
            <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
          )}
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500">
          Identificación fiscal
        </label>
        <input
          type="text"
          {...register('identificacion_fiscal')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500">Roles</label>
        <div className="mt-2 flex flex-wrap gap-2">
          {ROLES_DISPONIBLES.map((role) => (
            <label
              key={role}
              className={`inline-flex cursor-pointer items-center rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
                selectedRoles.includes(role)
                  ? 'bg-indigo-100 border-indigo-300 text-indigo-700'
                  : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={selectedRoles.includes(role)}
                onChange={() => handleRoleToggle(role)}
              />
              {role}
            </label>
          ))}
        </div>
        {errors.roles && (
          <p className="mt-1 text-xs text-red-600">{errors.roles.message}</p>
        )}
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500">Regional</label>
        <input
          type="text"
          {...register('regional')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500">
          Modalidad de facturación
        </label>
        <select
          {...register('modalidad_facturacion')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">Seleccionar</option>
          <option value="Factura">Factura</option>
          <option value="Recibo">Recibo</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-500">Banco</label>
          <input
            type="text"
            {...register('banco')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">CBU</label>
          <input
            type="text"
            {...register('cbu')}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-500">Alias CBU</label>
        <input
          type="text"
          {...register('alias_cbu')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
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
