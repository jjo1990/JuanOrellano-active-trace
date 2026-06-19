import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { AtrasadosTable } from '@/features/academico/components/AtrasadosTable'
import { RankingTable } from '@/features/academico/components/RankingTable'
import { NotasFinalesTable } from '@/features/academico/components/NotasFinalesTable'
import { TpsSinCorregirTable } from '@/features/academico/components/TpsSinCorregirTable'
import { useCalificaciones } from '@/features/academico/services/calificaciones'
import { useAtrasados } from '@/features/academico/services/analisis'

type Tab =
  | 'atrasados'
  | 'ranking'
  | 'notas-finales'
  | 'tps-sin-corregir'

const tabs: { key: Tab; label: string }[] = [
  { key: 'atrasados', label: 'Atrasados' },
  { key: 'ranking', label: 'Ranking' },
  { key: 'notas-finales', label: 'Notas Finales' },
  { key: 'tps-sin-corregir', label: 'TPs sin corregir' },
]

export function DashboardMateria() {
  const { id: materiaId } = useParams<{ id: string }>()
  const [activeTab, setActiveTab] = useState<Tab>('atrasados')

  const { data: calificaciones } = useCalificaciones(materiaId ?? '')
  const { data: atrasados } = useAtrasados(materiaId ?? '')

  const sinDatos =
    !calificaciones || calificaciones.length === 0

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Dashboard de materia
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Análisis de rendimiento y seguimiento de alumnos
        </p>
      </div>

      {sinDatos && (
        <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4">
          <p className="text-sm text-yellow-800">
            No hay datos importados. Importá calificaciones para ver el
            análisis.
          </p>
        </div>
      )}

      {!sinDatos && atrasados && (
        <div className="mb-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase text-gray-400">
              Alumnos atrasados
            </p>
            <p className="mt-1 text-2xl font-bold text-red-600">
              {atrasados.length}
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase text-gray-400">
              Total calificaciones
            </p>
            <p className="mt-1 text-2xl font-bold text-indigo-600">
              {calificaciones?.length ?? 0}
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-medium uppercase text-gray-400">
              Alumnos al día
            </p>
            <p className="mt-1 text-2xl font-bold text-green-600">
              {atrasados.filter((a) => a.estado === 'Al día').length}
            </p>
          </div>
        </div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-4 px-4" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.key
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4">
          {activeTab === 'atrasados' && (
            <AtrasadosTable materiaId={materiaId ?? ''} />
          )}
          {activeTab === 'ranking' && (
            <RankingTable materiaId={materiaId ?? ''} />
          )}
          {activeTab === 'notas-finales' && (
            <NotasFinalesTable materiaId={materiaId ?? ''} />
          )}
          {activeTab === 'tps-sin-corregir' && (
            <TpsSinCorregirTable materiaId={materiaId ?? ''} />
          )}
        </div>
      </div>
    </div>
  )
}
