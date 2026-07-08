import { useAuthStore } from '../store/slices/authSlice'
import { STORAGE_KEYS } from '../utils/constants'

export function useAuth() {
  const store = useAuthStore()

  return {
    user: store.user,
    isAuthenticated:
      store.isAuthenticated || Boolean(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)),
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    register: store.register,
    logout: store.logout,
    fetchMe: store.fetchMe,
    clearError: store.clearError,
  }
}
