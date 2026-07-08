import { apiClient } from './client'
import { ENDPOINTS } from './endpoints'
import type { AnalysisResult, AnalysisSummary } from '../types/analysis.types'

export const analysisApi = {
  async list(): Promise<AnalysisResult[]> {
    const { data: res } = await apiClient.get<AnalysisResult[]>(ENDPOINTS.analysis)
    return res
  },

  async getById(id: number): Promise<AnalysisResult> {
    const { data: res } = await apiClient.get<AnalysisResult>(ENDPOINTS.analysisDetail(id))
    return res
  },

  async getByDocument(documentId: number): Promise<AnalysisResult> {
    const { data: res } = await apiClient.get<AnalysisResult>(ENDPOINTS.analysisByDocument(documentId))
    return res
  },

  async summary(): Promise<AnalysisSummary> {
    const { data: res } = await apiClient.get<AnalysisSummary>(ENDPOINTS.analysisSummary)
    return res
  },

  async downloadReport(id: number): Promise<Blob> {
    const { data: res } = await apiClient.get<Blob>(ENDPOINTS.analysisReport(id), {
      responseType: 'blob',
    })
    return res
  },
}
