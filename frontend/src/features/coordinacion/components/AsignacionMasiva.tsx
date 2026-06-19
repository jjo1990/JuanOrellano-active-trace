import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/shared/services/api'
import type { DocenteSearchResult } from '@/features/coordinacion/types'

interface AsignacionMasivaProps {
  onAsignar: (asignaciones: {
    docente_id: string
    rol: string
    materia_id: string
    fecha_inicio: string
  }[]) => void
  isLoading: boolean
}

interface SelectedDocente {
  docente_id: string
  docente_nombre: string
}

async function searchDocentes(
  query: string
): Promise<DocenteSearchResult[]> {
  if (!query || query.length < 2) return []
  const response = await api.get<DocenteSearchResult[]>(
    '/api/usuarios/docentes',
    { params: { search: query } }
  )
  return response.data
}

const ROLES = ['PROFESOR', 'TUTOR', 'AUXILIAR', 'COORDINADOR']

export function AsignacionMasiva({
  onAsignar,
  isLoading,
}: AsignacionMasivaProps) {
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<SelectedDocente[]>([])
  const [rol, setRol] = useState('PROFESOR')
  const [materiaId, setMateriaId] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [showResults, setShowResults] = useState(false)

  const { data: searchResults, isFetching: isSearching } = useQuery({
    queryKey: ['docentes', 'search', search],
    queryFn: () => searchDocentes(search),
    enabled: search.length >= 2,
    staleTime: 30000,
  })

  const handleSearchChange = useCallback(
    (value: string) => {
      setSearch(value)
      setShowResults(value.length >= 2)
    },
    []
  )

  const handleSelectDocente = useCallback(
    (doc: DocenteSearchResult) => {
      if (!selected.find((s) => s.docente_id === doc.id)) {
        setSelected([
          ...selected,
          { docente_id: doc.id, docente_nombre: doc.nombre },
        ])
      }
      setSearch('')
      setShowResults(false)
    },
    [selected]
  )

  const handleRemove = useCallback(
    (id: string) => {
      setSelected(selected.filter((d) => d.docente_id !== id))
    },
    [selected]
  )

  const handleSubmit = useCallback(() => {
    if (selected.length === 0 || !materiaId || !fechaInicio) return
    onAsignar(
      selected.map((d) => ({
        docente_id: d.docente_id,
        rol,
        materia_id: materiaId,
        fecha_inicio: fechaInicio,
      }))
    )
  }, [selected, rol, materiaId, fechaInicio, onAsignar])

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <label className="block text-sm font-medium text-gray-700">
          Buscar docentes
        </label>
        <div className="relative mt-1">
          <input
            type="text"
            value={search}
            onChange={(e) => handleSearchChange(e.target.value)}
            placeholder="Nombre o apellido..."
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          {showResults && (
            <div className="absolute z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-md border border-gray-200 bg-white shadow-lg">
              {isSearching && (
                <div className="px-3 py-2 text-sm text-gray-500">
                  Buscando...
                </div>
              )}
              {searchResults?.map((doc) => (
                <button
                  key={doc.id}
                  type="button"
                  onClick={() => handleSelectDocente(doc)}
                  className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-indigo-50"
                >
                  <span className="font-medium text-gray-900">
                    {doc.nombre}
                  </span>
                  <span className="text-xs text-gray-400">
                    {doc.email}
                  </span>
                </button>
              ))}
              {searchResults?.length === 0 && !isSearching && (
                <div className="px-3 py-2 text-sm text-gray-400">
                  Sin resultados
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {selected.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-medium text-gray-700">
            Docentes seleccionados ({selected.length})
          </h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {selected.map((doc) => (
              <span
                key={doc.docente_id}
                className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700"
              >
                {doc.docente_nombre}
                <button
                  type="button"
                  onClick={() => handleRemove(doc.docente_id)}
                  className="ml-1 rounded-full p-0.5 hover:bg-indigo-100"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <label className="block text-sm font-medium text-gray-700">
            Rol
          </label>
          <select
            value={rol}
            onChange={(e) => setRol(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <label className="block text-sm font-medium text-gray-700">
            Materia ID
          </label>
          <input
            type="text"
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
            placeholder="ID de materia..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <label className="block text-sm font-medium text-gray-700">
            Fecha inicio
          </label>
          <input
            type="date"
            value={fechaInicio}
            onChange={(e) => setFechaInicio(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={
            isLoading ||
            selected.length === 0 ||
            !materiaId ||
            !fechaInicio
          }
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading
            ? 'Asignando...'
            : `Asignar ${selected.length} docente${selected.length !== 1 ? 's' : ''}`}
        </button>
      </div>
    </div>
  )
}
