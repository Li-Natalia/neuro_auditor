import { useAuthStore } from '../store/slices/authSlice'
import { STORAGE_KEYS } from '../utils/constants'

function isTokenValid(token: string | null): boolean {
  if (!token) return false
  try {
    const payload = token.split('.')[1]
    if (!payload) return false
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
    const decoded = JSON.parse(atob(padded)) as { exp?: number }
    if (typeof decoded.exp !== 'number') return false
    return decoded.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

export function useAuth() {
  const store = useAuthStore()

  return {
    user: store.user,
    isAuthenticated:
      store.isAuthenticated || isTokenValid(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)),
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    register: store.register,
    logout: store.logout,
    fetchMe: store.fetchMe,
    clearError: store.clearError,
  }
}
