export const APP_NAME = 'Нейроаудитор'
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/',
  UPLOAD: '/upload',
  ANALYSIS: '/analysis',
  ANALYSIS_DETAIL: '/analysis/:id',
  REPORTS: '/reports',
  CHAT: '/chat',
  PROFILE: '/profile',
} as const

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'fa_access_token',
  REFRESH_TOKEN: 'fa_refresh_token',
  THEME: 'fa_theme_mode',
} as const

export const ALLOWED_UPLOAD_EXTENSIONS = ['xlsx', 'xls'] as const
export const MAX_UPLOAD_SIZE_MB = 20

export type RiskLevel = 'critical' | 'medium' | 'low'

export const RISK_META: Record<RiskLevel, { label: string; color: string }> = {
  critical: { label: 'Критический', color: '#EF4444' },
  medium: { label: 'Средний', color: '#F59E0B' },
  low: { label: 'Низкий', color: '#10B981' },
}

export const REPORT_TEMPLATES = [
  { value: 'IFRS', label: 'МСФО (Международные стандарты)' },
  { value: 'RSBU', label: 'РСБУ (Российские стандарты)' },
] as const
