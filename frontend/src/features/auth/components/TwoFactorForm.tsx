import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useLocation, Navigate } from 'react-router-dom'
import {
  twoFactorSchema,
  type TwoFactorFormValues,
} from '@/features/auth/types/auth.types'
import { useLogin2fa } from '@/features/auth/hooks/useLogin2fa'

export function TwoFactorForm() {
  const location = useLocation()
  const challengeToken = (location.state as { challenge_token?: string } | null)
    ?.challenge_token

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TwoFactorFormValues>({
    resolver: zodResolver(twoFactorSchema),
  })

  const login2faMutation = useLogin2fa()

  if (!challengeToken) {
    return <Navigate to="/login" replace />
  }

  const onSubmit = (data: TwoFactorFormValues) => {
    login2faMutation.mutate({
      challenge_token: challengeToken,
      totp_code: data.totp_code,
    })
  }

  const errorMessage =
    login2faMutation.error instanceof Error
      ? login2faMutation.error.message
      : login2faMutation.isError
        ? 'Código inválido'
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
          htmlFor="totp_code"
          className="block text-sm font-medium text-gray-700"
        >
          Código de autenticación (6 dígitos)
        </label>
        <input
          id="totp_code"
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
          {...register('totp_code')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-center text-2xl tracking-widest shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="000000"
        />
        {errors.totp_code && (
          <p className="mt-1 text-sm text-red-600">
            {errors.totp_code.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={login2faMutation.isPending}
        className="flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {login2faMutation.isPending ? 'Verificando...' : 'Verificar'}
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
