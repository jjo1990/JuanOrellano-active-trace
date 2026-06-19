import { useState } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { UsuarioForm } from '@/features/admin/components/UsuarioForm'
import {
  useUsuarios,
  useCreateUsuario,
  useUpdateUsuario,
  useToggleUsuario,
} from '@/features/admin/services/usuarios'
import type { UsuarioTenant, UsuarioFormValues } from '@/features/admin/types'

export function GestionUsuarios() {
  const [search, setSearch] = useState('')
  const [rolFilter, setRolFilter] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingUsuario, setEditingUsuario] = useState<UsuarioTenant | null>(null)
  const [revealedCbus, setRevealedCbus] = useState<Record<string, ReturnType<typeof setTimeout>>>({})

  const { data, isLoading } = useUsuarios(
    rolFilter || undefined,
    search || undefined
  )
  const createUsuario = useCreateUsuario()
  const updateUsuario = useUpdateUsuario()
  const toggleUsuario = useToggleUsuario()

  const usuarios = data ?? []

  const maskCbu = (cbu?: string) => {
    if (!cbu) return '—'
    return '••••••••••••••••••' + cbu.slice(-4)
  }

  const handleRevealCbu = (id: string) => {
    if (revealedCbus[id]) {
      clearTimeout(revealedCbus[id])
      const newRevealed = { ...revealedCbus }
      delete newRevealed[id]
      setRevealedCbus(newRevealed)
    } else {
      const timer = setTimeout(() => {
        setRevealedCbus((prev) => {
          const next = { ...prev }
          delete next[id]
          return next
        })
      }, 30000)
      setRevealedCbus((prev) => ({ ...prev, [id]: timer }))
    }
  }

  const columns: Column<UsuarioTenant>[] = [
    {
      key: 'nombre',
      header: 'Nombre',
      sortable: true,
      accessor: (row) => row.nombre,
    },
    {
      key: 'email',
      header: 'Email',
      sortable: true,
      accessor: (row) => row.email,
    },
    {
      key: 'roles',
      header: 'Roles',
      accessor: (row) => (
        <div className="flex flex-wrap gap-1">
          {row.roles.map((r) => (
            <span
              key={r}
              className="inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700"
            >
              {r}
            </span>
          ))}
        </div>
      ),
    },
    {
      key: 'regional',
      header: 'Regional',
      accessor: (row) => row.regional ?? '—',
    },
    {
      key: 'cbu',
      header: 'CBU',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs">
            {revealedCbus[row.id] ? row.cbu : maskCbu(row.cbu)}
          </span>
          {row.cbu && (
            <button
              type="button"
              onClick={() => handleRevealCbu(row.id)}
              className="text-xs text-indigo-600 hover:text-indigo-800"
            >
              {revealedCbus[row.id] ? 'Ocultar' : 'Revelar'}
            </button>
          )}
        </div>
      ),
    },
    {
      key: 'estado',
      header: 'Estado',
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.activo
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {row.activo ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      accessor: (row) => (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              setEditingUsuario(row)
              setShowForm(true)
            }}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            Editar
          </button>
          <button
            type="button"
            onClick={() => toggleUsuario.mutate({ id: row.id, activo: !row.activo })}
            className={`text-xs ${
              row.activo
                ? 'text-red-600 hover:text-red-800'
                : 'text-green-600 hover:text-green-800'
            }`}
          >
            {row.activo ? 'Desactivar' : 'Activar'}
          </button>
        </div>
      ),
    },
  ]

  const handleSubmit = (data: UsuarioFormValues) => {
    if (editingUsuario) {
      updateUsuario.mutate(
        { id: editingUsuario.id, data },
        { onSuccess: () => { setShowForm(false); setEditingUsuario(null) } }
      )
    } else {
      createUsuario.mutate(data, {
        onSuccess: () => setShowForm(false),
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Gestión de usuarios
        </h1>
      </div>

      <div className="flex gap-4 rounded-lg border border-gray-200 bg-white p-4">
        <div className="flex-1">
          <label className="block text-xs font-medium text-gray-500">
            Búsqueda
          </label>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre o email..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500">Rol</label>
          <select
            value={rolFilter}
            onChange={(e) => setRolFilter(e.target.value)}
            className="mt-1 block rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">Todos</option>
            <option value="PROFESOR">PROFESOR</option>
            <option value="TUTOR">TUTOR</option>
            <option value="COORDINADOR">COORDINADOR</option>
            <option value="NEXO">NEXO</option>
            <option value="FINANZAS">FINANZAS</option>
            <option value="ADMIN">ADMIN</option>
          </select>
        </div>
      </div>

      {!showForm && (
        <button
          type="button"
          onClick={() => {
            setEditingUsuario(null)
            setShowForm(true)
          }}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Nuevo usuario
        </button>
      )}

      {showForm && (
        <UsuarioForm
          initialValues={editingUsuario ?? undefined}
          onSubmit={handleSubmit}
          onCancel={() => {
            setShowForm(false)
            setEditingUsuario(null)
          }}
          isLoading={createUsuario.isPending || updateUsuario.isPending}
        />
      )}

      <DataTable
        columns={columns}
        data={usuarios}
        isLoading={isLoading}
        getRowKey={(row) => row.id}
        emptyMessage="No hay usuarios registrados."
      />
    </div>
  )
}
