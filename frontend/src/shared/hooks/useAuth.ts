import { useContext } from 'react'
import { AuthContext } from '@/shared/contexts/AuthContext'
import type { AuthContextValue } from '@/shared/types/auth.types'

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
