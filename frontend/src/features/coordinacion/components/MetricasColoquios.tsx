import { useMetricasColoquios } from '@/features/coordinacion/services/coloquios'

export function MetricasColoquios() {
  const { data, isLoading } = useMetricasColoquios()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        <span className="ml-3 text-sm text-gray-500">
          Cargando métricas...
        </span>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="py-8 text-center text-sm text-gray-400">
        No hay datos de métricas disponibles.
      </div>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase text-gray-400">
          Total convocados
        </p>
        <p className="mt-1 text-2xl font-bold text-indigo-600">
          {data.total_convocados}
        </p>
      </div>
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase text-gray-400">
          Reservas confirmadas
        </p>
        <p className="mt-1 text-2xl font-bold text-green-600">
          {data.reservas_confirmadas}
        </p>
      </div>
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase text-gray-400">
          Turnos libres
        </p>
        <p className="mt-1 text-2xl font-bold text-yellow-600">
          {data.turnos_libres}
        </p>
      </div>
      <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <p className="text-xs font-medium uppercase text-gray-400">
          % Ocupación
        </p>
        <p className="mt-1 text-2xl font-bold text-blue-600">
          {data.porcentaje_ocupacion}%
        </p>
      </div>
    </div>
  )
}
