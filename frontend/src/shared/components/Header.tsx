import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/shared/hooks/useAuth'
import { useLogout } from '@/features/auth/hooks/useLogout'
import { useProfile } from '@/features/auth/hooks/useProfile'

export function Header() {
  const { user } = useAuth()
  const { data: profile } = useProfile()
  const logoutMutation = useLogout()
  const navigate = useNavigate()

  const displayName =
    profile?.nombre && profile?.apellidos
      ? `${profile.nombre} ${profile.apellidos}`
      : 'Usuario'

  const email = profile?.email ?? ''

  const handleLogout = () => {
    logoutMutation.mutate(undefined, {
      onSettled: () => {
        navigate('/login')
      },
    })
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-4 lg:px-6">
      <div className="ml-10 lg:ml-0">
        <span className="text-sm font-medium text-gray-900">{displayName}</span>
        {email && (
          <span className="ml-2 text-xs text-gray-500">{email}</span>
        )}
      </div>
      <div className="flex items-center gap-4">
        {user && (
          <span className="hidden text-xs text-gray-400 sm:inline">
            {user.roles.join(', ')}
          </span>
        )}
        <button
          type="button"
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="rounded-md px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
        >
          {logoutMutation.isPending ? 'Saliendo...' : 'Cerrar sesión'}
        </button>
      </div>
    </header>
  )
}
