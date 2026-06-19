import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import {
  forgotPasswordSchema,
  type ForgotPasswordFormValues,
} from '@/features/auth/types/auth.types'
import { useForgotPassword } from '@/features/auth/hooks/useForgotPassword'

export function ForgotPasswordForm() {
  const [submitted, setSubmitted] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
  })

  const forgotMutation = useForgotPassword()

  const onSubmit = (data: ForgotPasswordFormValues) => {
    forgotMutation.mutate(data, {
      onSuccess: () => {
        setSubmitted(true)
      },
      onError: () => {
        setSubmitted(true)
      },
    })
  }

  if (submitted) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-sm text-gray-600">
          Si el email está registrado, recibirás un enlace para recuperar tu
          contraseña.
        </p>
        <Link
          to="/login"
          className="text-sm text-indigo-600 hover:text-indigo-500"
        >
          Volver al inicio de sesión
        </Link>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <p className="text-sm text-gray-600">
        Ingresá tu email y te enviaremos un enlace para recuperar tu
        contraseña.
      </p>

      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700"
        >
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          {...register('email')}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={forgotMutation.isPending}
        className="flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {forgotMutation.isPending ? 'Enviando...' : 'Enviar enlace'}
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
