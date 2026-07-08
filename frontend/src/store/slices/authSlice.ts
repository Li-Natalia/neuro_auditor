import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../../api/authApi'
import { clearTokens } from '../../api/client'
import { STORAGE_KEYS } from '../../utils/constants'
import type { User } from '../../types/auth.types'
import type { LoginFormData, RegisterFormData } from '../../utils/validators'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (data: LoginFormData) => Promise<void>
  register: (data: RegisterFormData) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      async login(data) {
        set({ isLoading: true, error: null })
        try {
          const res = await authApi.login(data)
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, res.accessToken)
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, res.refreshToken)
          set({ user: res.user, isAuthenticated: true, isLoading: false })
        } catch (e) {
          set({ isLoading: false, error: (e as Error).message })
          throw e
        }
      },

      async register(data) {
        set({ isLoading: true, error: null })
        try {
          const res = await authApi.register(data)
          localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, res.accessToken)
          localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, res.refreshToken)
          set({ user: res.user, isAuthenticated: true, isLoading: false })
        } catch (e) {
          set({ isLoading: false, error: (e as Error).message })
          throw e
        }
      },

      logout() {
        clearTokens()
        set({ user: null, isAuthenticated: false })
      },

      async fetchMe() {
        set({ isLoading: true })
        try {
          const user = await authApi.me()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch {
          clearTokens()
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      clearError() {
        set({ error: null })
      },
    }),
    {
      name: 'fa-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    },
  ),
)
