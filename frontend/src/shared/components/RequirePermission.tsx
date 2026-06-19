import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'

interface RequirePermissionProps {
  permission: string
  children?: React.ReactNode
}

export function RequirePermission({
  permission,
  children,
}: RequirePermissionProps) {
  const { user } = useAuth()

  const hasPermission =
    user?.roles?.some(
      (role) =>
        // Simple match: role "PROFESOR" can access "calificaciones:importar"
        // In a real system, this would check actual permission claims from JWT
        role === permission.split(':')[0].toUpperCase() ||
        role === 'ADMIN' ||
        role === 'COORDINADOR'
    ) ?? false

  if (!hasPermission) {
    return <Navigate to="/app/unauthorized" replace />
  }

  if (children) return <>{children}</>

  return <Outlet />
}
