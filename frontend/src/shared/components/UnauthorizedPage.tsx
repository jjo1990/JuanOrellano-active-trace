import { Link } from 'react-router-dom'

export function UnauthorizedPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center">
      <h1 className="text-6xl font-bold text-gray-300">403</h1>
      <h2 className="mt-4 text-xl font-semibold text-gray-900">
        Acceso no autorizado
      </h2>
      <p className="mt-2 text-sm text-gray-600">
        No tiene permisos para acceder a esta sección.
      </p>
      <Link
        to="/app"
        className="mt-6 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
      >
        Volver al inicio
      </Link>
    </div>
  )
}
