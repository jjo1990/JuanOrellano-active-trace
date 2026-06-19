import { LoginForm } from '@/features/auth/components/LoginForm'

export function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">activia-trace</h1>
          <p className="mt-2 text-sm text-gray-600">
            Plataforma de gestión académica
          </p>
        </div>
        <div className="rounded-lg bg-white px-8 py-10 shadow-md">
          <h2 className="mb-6 text-xl font-semibold text-gray-900">
            Iniciar sesión
          </h2>
          <LoginForm />
        </div>
      </div>
    </div>
  )
}
