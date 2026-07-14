import { apiClient } from './client'
import { ENDPOINTS } from './endpoints'
import type { AuthResponse, User } from '../types/auth.types'
import type { LoginFormData, RegisterFormData } from '../utils/validators'

export const authApi = {
  async login(data: LoginFormData): Promise<AuthResponse> {
    const { data: res } = await apiClient.post<AuthResponse>(ENDPOINTS.login, data)
    return res
  },

  async register(data: RegisterFormData): Promise<AuthResponse> {
    const { data: res } = await apiClient.post<AuthResponse>(ENDPOINTS.register, data)
    return res
  },

  async refresh(refreshToken: string): Promise<{ accessToken: string }> {
    const { data: res } = await apiClient.post<{ accessToken: string }>(ENDPOINTS.refresh, {
      refreshToken,
    })
    return res
  },

  async me(): Promise<User> {
    const { data: res } = await apiClient.get<User>(ENDPOINTS.me)
    return res
  },

  async resetPassword(email: string): Promise<{ message: string }> {
    const { data: res } = await apiClient.post<{ message: string }>(ENDPOINTS.resetPassword, { email })
    return res
  },
}
