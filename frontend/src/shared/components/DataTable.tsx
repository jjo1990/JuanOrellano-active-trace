import { useState, useMemo, type ReactNode } from 'react'

export interface Column<T> {
  key: string
  header: string
  accessor: (row: T) => ReactNode
  sortable?: boolean
  className?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  isLoading?: boolean
  emptyMessage?: string
  getRowKey: (row: T) => string
}

export function DataTable<T>({
  columns,
  data,
  isLoading = false,
  emptyMessage = 'No hay datos disponibles.',
  getRowKey,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const sortedData = useMemo(() => {
    if (!sortKey) return data

    const column = columns.find((c) => c.key === sortKey)
    if (!column) return data

    return [...data].sort((a, b) => {
      const aVal = column.accessor(a)
      const bVal = column.accessor(b)

      const aStr = aVal != null ? String(aVal) : ''
      const bStr = bVal != null ? String(bVal) : ''

      const cmp = aStr.localeCompare(bStr, undefined, {
        numeric: true,
        sensitivity: 'base',
      })

      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [data, sortKey, sortDir, columns])

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        <span className="ml-3 text-sm text-gray-500">Cargando...</span>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={`px-4 py-3 text-left font-medium text-gray-700 ${
                  col.sortable ? 'cursor-pointer select-none hover:bg-gray-100' : ''
                } ${col.className ?? ''}`}
                onClick={() => col.sortable && handleSort(col.key)}
              >
                <div className="flex items-center gap-1">
                  {col.header}
                  {col.sortable && sortKey === col.key && (
                    <span className="text-xs text-indigo-600">
                      {sortDir === 'asc' ? '\u25B2' : '\u25BC'}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {sortedData.map((row) => (
            <tr key={getRowKey(row)} className="hover:bg-gray-50">
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`px-4 py-2.5 text-gray-700 ${col.className ?? ''}`}
                >
                  {col.accessor(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
