import { useAccionesPorDia } from '@/features/admin/services/auditoria'
import type { AuditoriaFilters } from '@/features/admin/types'

interface AuditoriaAccionesPorDiaProps {
  filters: AuditoriaFilters
}

export function AuditoriaAccionesPorDia({
  filters,
}: AuditoriaAccionesPorDiaProps) {
  const { data, isLoading } = useAccionesPorDia(filters)

  const acciones = data ?? []
  const maxCantidad = acciones.reduce(
    (max, item) => Math.max(max, item.cantidad),
    0
  )

  if (isLoading) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        Cargando...
      </div>
    )
  }

  if (acciones.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        No hay datos de acciones para el período seleccionado.
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {acciones.map((item) => {
        const porcentaje =
          maxCantidad > 0 ? (item.cantidad / maxCantidad) * 100 : 0
        return (
          <div key={item.fecha} className="flex items-center gap-3">
            <span className="w-24 text-xs text-gray-500">
              {new Date(item.fecha).toLocaleDateString('es-AR', {
                day: '2-digit',
                month: '2-digit',
              })}
            </span>
            <div className="flex-1">
              <div
                className="h-5 rounded bg-indigo-500 transition-all"
                style={{ width: `${porcentaje}%`, minWidth: '4px' }}
              />
            </div>
            <span className="w-12 text-right text-xs font-medium text-gray-700">
              {item.cantidad}
            </span>
          </div>
        )
      })}
    </div>
  )
}
