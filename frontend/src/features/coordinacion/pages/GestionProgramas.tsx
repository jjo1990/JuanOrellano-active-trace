import { useState, useCallback, type FormEvent } from 'react'
import { DataTable, type Column } from '@/shared/components/DataTable'
import { FechasAcademicasTable } from '@/features/coordinacion/components/FechasAcademicasTable'
import {
  useProgramas,
  useUploadPrograma,
  useCreateFechaAcademica,
} from '@/features/coordinacion/services/programas'
import type {
  Programa,
  FechaAcademicaFormValues,
} from '@/features/coordinacion/types'

type Tab = 'programas' | 'fechas'

const tabs: { key: Tab; label: string }[] = [
  { key: 'programas', label: 'Programas' },
  { key: 'fechas', label: 'Fechas académicas' },
]

export function GestionProgramas() {
  const [activeTab, setActiveTab] = useState<Tab>('programas')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [archivo, setArchivo] = useState<File | null>(null)
  const [showFechaForm, setShowFechaForm] = useState(false)
  const [message, setMessage] = useState<{
    text: string
    type: 'success' | 'error'
  } | null>(null)

  const { data, isLoading } = useProgramas(cohorteId || undefined)
  const uploadMutation = useUploadPrograma()
  const createFechaMutation = useCreateFechaAcademica()

  const showMessage = useCallback(
    (text: string, type: 'success' | 'error') => {
      setMessage({ text, type })
      setTimeout(() => setMessage(null), 5000)
    },
    []
  )

  const handleUpload = useCallback(
    (e: FormEvent) => {
      e.preventDefault()
      if (!archivo || !materiaId || !carreraId || !cohorteId) return

      const formData = new FormData()
      formData.append('archivo', archivo)
      formData.append('materia_id', materiaId)
      formData.append('carrera_id', carreraId)
      formData.append('cohorte_id', cohorteId)

      uploadMutation.mutate(formData, {
        onSuccess: () => {
          showMessage('Programa subido.', 'success')
          setArchivo(null)
        },
        onError: () => showMessage('Error al subir programa.', 'error'),
      })
    },
    [archivo, materiaId, carreraId, cohorteId, uploadMutation, showMessage]
  )

  const [fechaForm, setFechaForm] = useState<
    Partial<FechaAcademicaFormValues>
  >({
    tipo: 'Parcial',
    numero: 1,
    fecha: '',
    materia_id: '',
    cohorte_id: '',
    comentario: '',
  })

  const handleCreateFecha = useCallback(
    (e: FormEvent) => {
      e.preventDefault()
      const data = fechaForm as FechaAcademicaFormValues
      if (!data.fecha || !data.materia_id || !data.cohorte_id) return

      createFechaMutation.mutate(data, {
        onSuccess: () => {
          showMessage('Fecha académica creada.', 'success')
          setShowFechaForm(false)
        },
        onError: () =>
          showMessage('Error al crear fecha.', 'error'),
      })
    },
    [fechaForm, createFechaMutation, showMessage]
  )

  const columns: Column<Programa>[] = [
    {
      key: 'archivo',
      header: 'Archivo',
      sortable: true,
      accessor: (row) => row.archivo_nombre,
    },
    {
      key: 'materia',
      header: 'Materia',
      sortable: true,
      accessor: (row) => row.materia_nombre ?? row.materia_id,
    },
    {
      key: 'carrera',
      header: 'Carrera',
      sortable: true,
      accessor: (row) => row.carrera_nombre ?? row.carrera_id,
    },
    {
      key: 'cohorte',
      header: 'Cohorte',
      sortable: true,
      accessor: (row) => row.cohorte_nombre ?? row.cohorte_id,
    },
    {
      key: 'fecha',
      header: 'Subido',
      sortable: true,
      accessor: (row) => row.creado_en.slice(0, 10),
    },
  ]

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Programas y fechas
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Programas de materia y fechas académicas
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowFechaForm(true)}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            + Nueva fecha
          </button>
        </div>
      </div>

      {message && (
        <div
          className={`mb-4 rounded-md px-4 py-3 text-sm ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          {message.text}
        </div>
      )}

      {/* Upload form */}
      <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="text-sm font-medium text-gray-900">
          Subir programa
        </h3>
        <form onSubmit={handleUpload} className="mt-3 grid gap-3 sm:grid-cols-5">
          <div>
            <label className="block text-xs font-medium text-gray-500">
              Materia
            </label>
            <input
              type="text"
              value={materiaId}
              onChange={(e) => setMateriaId(e.target.value)}
              placeholder="ID materia..."
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500">
              Carrera
            </label>
            <input
              type="text"
              value={carreraId}
              onChange={(e) => setCarreraId(e.target.value)}
              placeholder="ID carrera..."
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500">
              Cohorte
            </label>
            <input
              type="text"
              value={cohorteId}
              onChange={(e) => setCohorteId(e.target.value)}
              placeholder="ID cohorte..."
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500">
              Archivo (PDF/DOC)
            </label>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={(e) =>
                setArchivo(e.target.files?.[0] ?? null)
              }
              className="mt-1 block w-full text-sm text-gray-500 file:mr-3 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1 file:text-xs file:font-medium file:text-indigo-700"
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={
                uploadMutation.isPending ||
                !archivo ||
                !materiaId ||
                !carreraId ||
                !cohorteId
              }
              className="w-full rounded-md bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploadMutation.isPending ? 'Subiendo...' : 'Subir'}
            </button>
          </div>
        </form>
      </div>

      {showFechaForm && (
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-6">
          <h3 className="text-sm font-medium text-gray-900">
            Nueva fecha académica
          </h3>
          <form
            onSubmit={handleCreateFecha}
            className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-5"
          >
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Tipo
              </label>
              <select
                value={fechaForm.tipo}
                onChange={(e) =>
                  setFechaForm({ ...fechaForm, tipo: e.target.value as FechaAcademicaFormValues['tipo'] })
                }
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="Parcial">Parcial</option>
                <option value="TP">TP</option>
                <option value="Coloquio">Coloquio</option>
                <option value="Recuperatorio">Recuperatorio</option>
                <option value="Otro">Otro</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Número
              </label>
              <input
                type="number"
                value={fechaForm.numero ?? ''}
                onChange={(e) =>
                  setFechaForm({
                    ...fechaForm,
                    numero: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
                min={1}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Fecha
              </label>
              <input
                type="date"
                value={fechaForm.fecha}
                onChange={(e) =>
                  setFechaForm({ ...fechaForm, fecha: e.target.value })
                }
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500">
                Materia
              </label>
              <input
                type="text"
                value={fechaForm.materia_id}
                onChange={(e) =>
                  setFechaForm({
                    ...fechaForm,
                    materia_id: e.target.value,
                  })
                }
                placeholder="ID materia..."
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={
                  createFechaMutation.isPending ||
                  !fechaForm.fecha ||
                  !fechaForm.materia_id ||
                  !fechaForm.cohorte_id
                }
                className="w-full rounded-md bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {createFechaMutation.isPending ? 'Creando...' : 'Crear'}
              </button>
            </div>
          </form>
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
          {activeTab === 'programas' && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-500">
                  Cohorte
                </label>
                <input
                  type="text"
                  value={cohorteId}
                  onChange={(e) => setCohorteId(e.target.value)}
                  placeholder="ID cohorte..."
                  className="mt-1 block w-40 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
              <DataTable
                columns={columns}
                data={data ?? []}
                isLoading={isLoading}
                emptyMessage="No hay programas subidos."
                getRowKey={(row) => row.id}
              />
            </div>
          )}

          {activeTab === 'fechas' && (
            <FechasAcademicasTable cohorteId={cohorteId} />
          )}
        </div>
      </div>
    </div>
  )
}
