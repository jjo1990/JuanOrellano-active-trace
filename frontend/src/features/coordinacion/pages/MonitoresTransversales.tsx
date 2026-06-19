import { useState } from 'react'
import { MonitorGeneralTable } from '@/features/coordinacion/components/MonitorGeneralTable'
import { MonitorPorDocente } from '@/features/coordinacion/components/MonitorPorDocente'

type Tab = 'general' | 'por-docente'

const tabs: { key: Tab; label: string }[] = [
  { key: 'general', label: 'General' },
  { key: 'por-docente', label: 'Por Docente' },
]

export function MonitoresTransversales() {
  const [activeTab, setActiveTab] = useState<Tab>('general')

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Monitores transversales
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Vista general de todas las materias y seguimiento por docente
        </p>
      </div>

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
          {activeTab === 'general' && <MonitorGeneralTable />}
          {activeTab === 'por-docente' && <MonitorPorDocente />}
        </div>
      </div>
    </div>
  )
}
