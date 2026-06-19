import { useState, type FormEvent } from 'react'
import type { MonitorFilters as MonitorFiltersType } from '@/features/academico/types'

interface MonitorFiltersProps {
  filters: MonitorFiltersType
  onChange: (filters: MonitorFiltersType) => void
}

export function MonitorFilters({ filters, onChange }: MonitorFiltersProps) {
  const [search, setSearch] = useState(filters.search ?? '')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onChange({ ...filters, search: search || undefined })
  }

  const handleSearchClear = () => {
    setSearch('')
    onChange({ ...filters, search: undefined })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-wrap items-end gap-3 rounded-lg border border-gray-200 bg-white p-4"
    >
      <div className="min-w-0 flex-1">
        <label
          htmlFor="monitor-search"
          className="block text-xs font-medium text-gray-500"
        >
          Buscar alumno
        </label>
        <input
          id="monitor-search"
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Nombre o apellido..."
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="min-w-0 flex-1">
        <label
          htmlFor="filter-materia"
          className="block text-xs font-medium text-gray-500"
        >
          Materia
        </label>
        <input
          id="filter-materia"
          type="text"
          value={filters.materia_id ?? ''}
          onChange={(e) =>
            onChange({
              ...filters,
              materia_id: e.target.value || undefined,
            })
          }
          placeholder="ID de materia..."
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="min-w-0 flex-1">
        <label
          htmlFor="filter-comision"
          className="block text-xs font-medium text-gray-500"
        >
          Comisión
        </label>
        <input
          id="filter-comision"
          type="text"
          value={filters.comision_id ?? ''}
          onChange={(e) =>
            onChange({
              ...filters,
              comision_id: e.target.value || undefined,
            })
          }
          placeholder="ID de comisi\u00F3n..."
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Filtrar
        </button>
        <button
          type="button"
          onClick={handleSearchClear}
          className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Limpiar
        </button>
      </div>
    </form>
  )
}
