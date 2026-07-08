import { useAnalysisStore } from '../store/slices/analysisSlice'

export function useAnalysis() {
  const store = useAnalysisStore()
  return {
    list: store.list,
    current: store.current,
    summary: store.summary,
    isLoading: store.isLoading,
    error: store.error,
    fetchList: store.fetchList,
    fetchById: store.fetchById,
    fetchByDocument: store.fetchByDocument,
    fetchSummary: store.fetchSummary,
    downloadReport: store.downloadReport,
    clearError: store.clearError,
  }
}
