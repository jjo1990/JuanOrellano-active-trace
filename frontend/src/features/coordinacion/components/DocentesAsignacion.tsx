import type { AsignacionDocenteItem } from '@/features/coordinacion/types'
import { AsignacionMasiva } from '@/features/coordinacion/components/AsignacionMasiva'
import { useAsignarDocentes } from '@/features/coordinacion/services/equipos'

interface DocentesAsignacionProps {
  cohorteId: string
  asignados: AsignacionDocenteItem[]
  onAsignar: (asignaciones: AsignacionDocenteItem[]) => void
}

export function DocentesAsignacion({
  cohorteId,
  asignados,
  onAsignar,
}: DocentesAsignacionProps) {
  const mutation = useAsignarDocentes()

  const handleAsignar = (
    items: {
      docente_id: string
      rol: string
      materia_id: string
      fecha_inicio: string
    }[]
  ) => {
    mutation.mutate(
      { cohorte_id: cohorteId, asignaciones: items },
      {
        onSuccess: () => {
          const nuevos: AsignacionDocenteItem[] = items.map((i) => ({
            docente_id: i.docente_id,
            docente_nombre: i.docente_id,
            rol: i.rol,
            materia_id: i.materia_id,
            materia_nombre: i.materia_id,
            fecha_inicio: i.fecha_inicio,
          }))
          onAsignar([...asignados, ...nuevos])
        },
      }
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-gray-900">
        Paso 2: Asignar docentes
      </h3>
      <p className="text-sm text-gray-500">
        Asigná los docentes a las materias y roles correspondientes.
      </p>

      <AsignacionMasiva
        onAsignar={handleAsignar}
        isLoading={mutation.isPending}
      />

      {asignados.length > 0 && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <h4 className="text-sm font-medium text-green-800">
            {asignados.length} docentes asignados
          </h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {asignados.map((a, idx) => (
              <span
                key={idx}
                className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700"
              >
                {a.docente_nombre} → {a.rol} en {a.materia_nombre}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
