import { ResetPasswordForm } from '@/features/auth/components/ResetPasswordForm'

export function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">activia-trace</h1>
          <p className="mt-2 text-sm text-gray-600">
            Nueva contraseña
          </p>
        </div>
        <div className="rounded-lg bg-white px-8 py-10 shadow-md">
          <h2 className="mb-6 text-xl font-semibold text-gray-900">
            Restablecer contraseña
          </h2>
          <ResetPasswordForm />
        </div>
      </div>
    </div>
  )
}
