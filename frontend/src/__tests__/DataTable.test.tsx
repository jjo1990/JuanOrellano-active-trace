import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DataTable, type Column } from '@/shared/components/DataTable'

interface TestRow {
  id: string
  name: string
  value: number
}

const columns: Column<TestRow>[] = [
  {
    key: 'name',
    header: 'Name',
    sortable: true,
    accessor: (row) => row.name,
  },
  {
    key: 'value',
    header: 'Value',
    sortable: true,
    accessor: (row) => row.value,
  },
]

const data: TestRow[] = [
  { id: '1', name: 'Charlie', value: 30 },
  { id: '2', name: 'Alice', value: 10 },
  { id: '3', name: 'Bob', value: 20 },
]

describe('DataTable', () => {
  it('renders data rows', () => {
    render(
      <DataTable
        columns={columns}
        data={data}
        getRowKey={(row) => row.id}
      />
    )

    expect(screen.getByText('Charlie')).toBeInTheDocument()
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
  })

  it('shows empty message when no data', () => {
    render(
      <DataTable
        columns={columns}
        data={[]}
        getRowKey={(row) => row.id}
        emptyMessage="No hay datos."
      />
    )

    expect(screen.getByText('No hay datos.')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    render(
      <DataTable
        columns={columns}
        data={data}
        isLoading
        getRowKey={(row) => row.id}
      />
    )

    expect(screen.getByText('Cargando...')).toBeInTheDocument()
  })

  it('renders column headers', () => {
    render(
      <DataTable
        columns={columns}
        data={data}
        getRowKey={(row) => row.id}
      />
    )

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Value')).toBeInTheDocument()
  })
})
