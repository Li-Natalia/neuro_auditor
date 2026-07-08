import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { STORAGE_KEYS } from '../../utils/constants'

type ThemeMode = 'light' | 'dark'

interface AppNotification {
  id: string
  message: string
  severity: 'success' | 'error' | 'warning' | 'info'
}

interface UIState {
  mode: ThemeMode
  sidebarOpen: boolean
  notifications: AppNotification[]
  toggleTheme: () => void
  setTheme: (mode: ThemeMode) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  notify: (message: string, severity?: AppNotification['severity']) => void
  dismissNotification: (id: string) => void
}

const initialMode: ThemeMode =
  (localStorage.getItem(STORAGE_KEYS.THEME) as ThemeMode) || 'light'

export const useThemeStore = create<UIState>()(
  persist(
    (set) => ({
      mode: initialMode,
      sidebarOpen: true,
      notifications: [],

      toggleTheme() {
        set((s) => {
          const next = s.mode === 'light' ? 'dark' : 'light'
          localStorage.setItem(STORAGE_KEYS.THEME, next)
          return { mode: next }
        })
      },
      setTheme(mode) {
        localStorage.setItem(STORAGE_KEYS.THEME, mode)
        set({ mode })
      },
      toggleSidebar() {
        set((s) => ({ sidebarOpen: !s.sidebarOpen }))
      },
      setSidebarOpen(open) {
        set({ sidebarOpen: open })
      },
      notify(message, severity = 'info') {
        const id = Date.now().toString(36)
        set((s) => ({ notifications: [...s.notifications, { id, message, severity }] }))
        setTimeout(() => {
          set((s) => ({ notifications: s.notifications.filter((n) => n.id !== id) }))
        }, 5000)
      },
      dismissNotification(id) {
        set((s) => ({ notifications: s.notifications.filter((n) => n.id !== id) }))
      },
    }),
    { name: 'fa-ui' },
  ),
)
