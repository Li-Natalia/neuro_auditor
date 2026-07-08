export type UserRole = 'admin' | 'auditor' | 'viewer'

export interface User {
  id: number
  email: string
  name: string
  role: UserRole
  avatarUrl?: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  tokenType?: string
}

export interface AuthResponse extends AuthTokens {
  user: User
}
