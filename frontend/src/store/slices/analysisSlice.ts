import { create } from 'zustand'
import { analysisApi } from '../../api/analysisApi'
import type { AnalysisResult, AnalysisSummary } from '../../types/analysis.types'
import { getErrorMessage } from '../../utils/helpers'

interface AnalysisState {
  list: AnalysisResult[]
  current: AnalysisResult | null
  summary: AnalysisSummary | null
  isLoading: boolean
  error: string | null
  fetchList: () => Promise<void>
  fetchById: (id: number) => Promise<void>
  fetchByDocument: (documentId: number) => Promise<void>
  fetchSummary: () => Promise<void>
  downloadReport: (id: number) => Promise<Blob | undefined>
  clearError: () => void
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  list: [],
  current: null,
  summary: null,
  isLoading: false,
  error: null,

  async fetchList() {
    set({ isLoading: true, error: null })
    try {
      const list = await analysisApi.list()
      set({ list, isLoading: false })
    } catch (e) {
      set({ isLoading: false, error: getErrorMessage(e) })
    }
  },

  async fetchById(id) {
    set({ isLoading: true, error: null })
    try {
      const current = await analysisApi.getById(id)
      set({ current, isLoading: false })
    } catch (e) {
      set({ isLoading: false, error: getErrorMessage(e) })
    }
  },

  async fetchByDocument(documentId) {
    set({ isLoading: true, error: null })
    try {
      const current = await analysisApi.getByDocument(documentId)
      set({ current, isLoading: false })
    } catch (e) {
      set({ isLoading: false, error: getErrorMessage(e) })
    }
  },

  async fetchSummary() {
    set({ isLoading: true, error: null })
    try {
      const summary = await analysisApi.summary()
      set({ summary, isLoading: false })
    } catch (e) {
      set({ isLoading: false, error: getErrorMessage(e) })
    }
  },

  async downloadReport(id) {
    try {
      return await analysisApi.downloadReport(id)
    } catch (e) {
      set({ error: getErrorMessage(e) })
    }
  },

  clearError() {
    set({ error: null })
  },
}))
