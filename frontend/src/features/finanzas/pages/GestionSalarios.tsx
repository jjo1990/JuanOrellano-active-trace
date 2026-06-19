import { useState } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { SalarioBaseForm } from '@/features/finanzas/components/SalarioBaseForm'
import { PlusForm } from '@/features/finanzas/components/PlusForm'
import {
  useSalariosBase,
  useCreateSalarioBase,
  useUpdateSalarioBase,
  useDeactivateSalarioBase,
  usePlus,
  useCreatePlus,
  useUpdatePlus,
  useDeactivatePlus,
} from '@/features/finanzas/services/salarios'
import type {
  SalarioBase,
  SalarioBaseFormValues,
  Plus,
  PlusFormValues,
} from '@/features/finanzas/types'
import { useAuth } from '@/shared/hooks/useAuth'

type Tab = 'bases' | 'plus'

export function GestionSalarios() {
  const [tab, setTab] = useState<Tab>('bases')
  const [showBaseForm, setShowBaseForm] = useState(false)
  const [editingBase, setEditingBase] = useState<SalarioBase | null>(null)
  const [showPlusForm, setShowPlusForm] = useState(false)
  const [editingPlus, setEditingPlus] = useState<Plus | null>(null)
  const [plusError, setPlusError] = useState<string>()

  const { data: salariosBase, isLoading: basesLoading } = useSalariosBase()
  const { data: plus, isLoading: plusLoading } = usePlus()
  const createBase = useCreateSalarioBase()
  const updateBase = useUpdateSalarioBase()
  const deactivateBase = useDeactivateSalarioBase()
  const createPlus = useCreatePlus()
  const updatePlus = useUpdatePlus()
  const deactivatePlus = useDeactivatePlus()

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
      minimumFractionDigits: 2,
    }).format(value)

  const baseColumns: Column<SalarioBase>[] = [
    {
      key: 'rol',
      header: 'Rol',
      sortable: true,
      accessor: (row) => row.rol,
    },
    {
      key: 'monto',
      header: 'Monto',
      sortable: true,
      accessor: (row) => formatCurrency(row.monto),
    },
    {
      key: 'vigencia_desde',
      header: 'Vigencia desde',
      sortable: true,
      accessor: (row) =>
        new Date(row.vigencia_desde).toLocaleDateString('es-AR'),
    },
    {
      key: 'vigencia_hasta',
      header: 'Vigencia hasta',
      accessor: (row) =>
        row.vigencia_hasta
          ? new Date(row.vigencia_hasta).toLocaleDateString('es-AR')
          : '—',
    },
    {
      key: 'activo',
      header: 'Estado',
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.activo
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-600'
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
              setEditingBase(row)
              setShowBaseForm(true)
            }}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            Editar
          </button>
          {row.activo && (
            <button
              type="button"
              onClick={() => deactivateBase.mutate(row.id)}
              className="text-xs text-red-600 hover:text-red-800"
            >
              Desactivar
            </button>
          )}
        </div>
      ),
    },
  ]

  const plusColumns: Column<Plus>[] = [
    {
      key: 'clave',
      header: 'Clave',
      sortable: true,
      accessor: (row) => row.clave,
    },
    {
      key: 'rol',
      header: 'Rol',
      sortable: true,
      accessor: (row) => row.rol,
    },
    {
      key: 'descripcion',
      header: 'Descripción',
      accessor: (row) => row.descripcion,
    },
    {
      key: 'monto',
      header: 'Monto / %',
      accessor: (row) =>
        row.porcentaje != null
          ? `${row.porcentaje}%`
          : formatCurrency(row.monto ?? 0),
    },
    {
      key: 'vigencia_desde',
      header: 'Vigencia desde',
      sortable: true,
      accessor: (row) =>
        new Date(row.vigencia_desde).toLocaleDateString('es-AR'),
    },
    {
      key: 'vigencia_hasta',
      header: 'Vigencia hasta',
      accessor: (row) =>
        row.vigencia_hasta
          ? new Date(row.vigencia_hasta).toLocaleDateString('es-AR')
          : '—',
    },
    {
      key: 'activo',
      header: 'Estado',
      accessor: (row) => (
        <span
          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
            row.activo
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-600'
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
              setEditingPlus(row)
              setShowPlusForm(true)
            }}
            className="text-xs text-indigo-600 hover:text-indigo-800"
          >
            Editar
          </button>
          {row.activo && (
            <button
              type="button"
              onClick={() => deactivatePlus.mutate(row.id)}
              className="text-xs text-red-600 hover:text-red-800"
            >
              Desactivar
            </button>
          )}
        </div>
      ),
    },
  ]

  const handleBaseSubmit = (data: SalarioBaseFormValues) => {
    if (editingBase) {
      updateBase.mutate(
        { id: editingBase.id, data },
        { onSuccess: () => { setShowBaseForm(false); setEditingBase(null) } }
      )
    } else {
      createBase.mutate(data, {
        onSuccess: () => setShowBaseForm(false),
      })
    }
  }

  const handlePlusSubmit = (data: PlusFormValues) => {
    setPlusError(undefined)
    if (editingPlus) {
      updatePlus.mutate(
        { id: editingPlus.id, data },
        {
          onSuccess: () => { setShowPlusForm(false); setEditingPlus(null) },
          onError: (err: Error) =>
            setPlusError(err.message || 'Error al guardar plus'),
        }
      )
    } else {
      createPlus.mutate(data, {
        onSuccess: () => setShowPlusForm(false),
        onError: (err: Error) =>
          setPlusError(err.message || 'Error al crear plus'),
      })
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Grilla salarial</h1>
      </div>

      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-4">
          <button
            type="button"
            onClick={() => setTab('bases')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === 'bases'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Salarios Base
          </button>
          <button
            type="button"
            onClick={() => setTab('plus')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === 'plus'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Plus
          </button>
        </nav>
      </div>

      {tab === 'bases' && (
        <div className="space-y-4">
          {!showBaseForm && (
            <button
              type="button"
              onClick={() => {
                setEditingBase(null)
                setShowBaseForm(true)
              }}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Nuevo salario base
            </button>
          )}

          {showBaseForm && (
            <SalarioBaseForm
              initialValues={editingBase ?? undefined}
              onSubmit={handleBaseSubmit}
              onCancel={() => {
                setShowBaseForm(false)
                setEditingBase(null)
              }}
              isLoading={createBase.isPending || updateBase.isPending}
            />
          )}

          <DataTable
            columns={baseColumns}
            data={salariosBase ?? []}
            isLoading={basesLoading}
            getRowKey={(row) => row.id}
            emptyMessage="No hay salarios base configurados."
          />
        </div>
      )}

      {tab === 'plus' && (
        <div className="space-y-4">
          {!showPlusForm && (
            <button
              type="button"
              onClick={() => {
                setEditingPlus(null)
                setShowPlusForm(true)
              }}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Nuevo plus
            </button>
          )}

          {showPlusForm && (
            <PlusForm
              initialValues={editingPlus ?? undefined}
              onSubmit={handlePlusSubmit}
              onCancel={() => {
                setShowPlusForm(false)
                setEditingPlus(null)
                setPlusError(undefined)
              }}
              isLoading={createPlus.isPending || updatePlus.isPending}
              serverError={plusError}
            />
          )}

          <DataTable
            columns={plusColumns}
            data={plus ?? []}
            isLoading={plusLoading}
            getRowKey={(row) => row.id}
            emptyMessage="No hay plus configurados."
          />
        </div>
      )}
    </div>
  )
}
