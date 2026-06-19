import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useSearchParams, Navigate } from 'react-router-dom'
import {
  resetPasswordSchema,
  type ResetPasswordFormValues,
} from '@/features/auth/types/auth.types'
import { useResetPassword } from '@/features/auth/hooks/useResetPassword'

export function ResetPasswordForm() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
  })

  const resetMutation = useResetPassword()

  if (!token) {
    return <Navigate to="/login" replace />
  }

  if (resetMutation.isSuccess) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-sm text-green-600 font-medium">
          Contraseña actualizada correctamente.
        </p>
        <Link
          to="/login"
          className="text-sm text-indigo-600 hover:text-indigo-500"
        >
          Ir al inicio de sesión
        </Link>
      </div>
    )
  }

  const onSubmit = (data: ResetPasswordFormValues) => {
    resetMutation.mutate({
      token,
      new_password: data.new_password,
    })
  }

  const errorMessage =
    resetMutation.error instanceof Error
      ? resetMutation.error.message
      : resetMutation.isError
        ? 'El enlace es inválido o ha expirado.'
        : null

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {errorMessage && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
          {errorMessage}
        </div>
      )}

      <div>
        <label
          htmlFor="new_password"
          className="block text-sm font-medium text-gray-700"
        >
          Nueva contraseña
        </label>
        <input
          id="new_password"
          type="password"
          autoComplete="new-password"
          {...register('new_password')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.new_password && (
          <p className="mt-1 text-sm text-red-600">
            {errors.new_password.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="confirm_password"
          className="block text-sm font-medium text-gray-700"
        >
          Confirmar contraseña
        </label>
        <input
          id="confirm_password"
          type="password"
          autoComplete="new-password"
          {...register('confirm_password')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.confirm_password && (
          <p className="mt-1 text-sm text-red-600">
            {errors.confirm_password.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={resetMutation.isPending}
        className="flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {resetMutation.isPending ? 'Actualizando...' : 'Actualizar contraseña'}
      </button>

      <div className="text-center">
        <Link
          to="/login"
          className="text-sm text-indigo-600 hover:text-indigo-500"
        >
          Volver al inicio de sesión
        </Link>
      </div>
    </form>
  )
}
