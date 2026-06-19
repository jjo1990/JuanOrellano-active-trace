import { useAuth } from '@/shared/hooks/useAuth'

export function DashboardPage() {
  const { user } = useAuth()

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">
        Bienvenido/a, {user?.nombre ?? 'Usuario'}
      </h1>
      <p className="mt-2 text-gray-600">
        Plataforma de gestión académica y trazabilidad de actividades
        estudiantiles.
      </p>
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-medium text-gray-900">Actividad reciente</h3>
          <p className="mt-2 text-sm text-gray-500">
            No hay actividad reciente para mostrar.
          </p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-medium text-gray-900">Accesos rápidos</h3>
          <p className="mt-2 text-sm text-gray-500">
            Las funcionalidades se irán habilitando progresivamente.
          </p>
        </div>
      </div>
    </div>
  )
}
