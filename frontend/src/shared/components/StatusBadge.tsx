import type {
  EstadoEnvio,
  EstadoAlumno,
} from '@/features/academico/types'

interface StatusBadgeProps {
  estado: EstadoEnvio | EstadoAlumno | 'Aprobado' | 'Desaprobado'
}

const variantMap: Record<
  string,
  { bg: string; text: string; label: string }
> = {
  Pendiente: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-800',
    label: 'Pendiente',
  },
  Enviando: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    label: 'Enviando',
  },
  Enviado: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    label: 'Enviado',
  },
  Error: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    label: 'Error',
  },
  Cancelado: {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    label: 'Cancelado',
  },
  Atrasado: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    label: 'Atrasado',
  },
  'Al día': {
    bg: 'bg-green-100',
    text: 'text-green-800',
    label: 'Al día',
  },
  'Sin datos': {
    bg: 'bg-gray-100',
    text: 'text-gray-600',
    label: 'Sin datos',
  },
  Aprobado: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    label: 'Aprobado',
  },
  Desaprobado: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    label: 'Desaprobado',
  },
}

export function StatusBadge({ estado }: StatusBadgeProps) {
  const variant = variantMap[estado] ?? {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    label: estado,
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variant.bg} ${variant.text}`}
    >
      {variant.label}
    </span>
  )
}
