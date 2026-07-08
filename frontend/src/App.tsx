import { useEffect } from 'react'
import { useAuthStore } from './store/slices/authSlice'
import { STORAGE_KEYS } from './utils/constants'
import { AppRoutes } from './routes/AppRoutes'
import { ErrorBoundary } from './components/common/ErrorBoundary/ErrorBoundary'

export default function App() {
  const fetchMe = useAuthStore((s) => s.fetchMe)

  useEffect(() => {
    if (localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)) {
      void fetchMe()
    }
  }, [fetchMe])

  return (
    <ErrorBoundary>
      <AppRoutes />
    </ErrorBoundary>
  )
}
