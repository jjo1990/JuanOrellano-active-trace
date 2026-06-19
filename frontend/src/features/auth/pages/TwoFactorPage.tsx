import { TwoFactorForm } from '@/features/auth/components/TwoFactorForm'

export function TwoFactorPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">activia-trace</h1>
          <p className="mt-2 text-sm text-gray-600">
            Verificación en dos pasos
          </p>
        </div>
        <div className="rounded-lg bg-white px-8 py-10 shadow-md">
          <h2 className="mb-6 text-xl font-semibold text-gray-900">
            Código de autenticación
          </h2>
          <p className="mb-4 text-sm text-gray-600">
            Ingresá el código de 6 dígitos generado por tu aplicación de
            autenticación.
          </p>
          <TwoFactorForm />
        </div>
      </div>
    </div>
  )
}
