import { apiClient } from './client'
import { ENDPOINTS } from './endpoints'
import type { FinancialDocument, UploadResponse, DocumentTemplate } from '../types/document.types'

export interface UploadParams {
  file: File
  template: DocumentTemplate
  onProgress?: (percent: number) => void
}

export const documentsApi = {
  async upload({ file, template, onProgress }: UploadParams): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('template', template)
    const { data: res } = await apiClient.post<UploadResponse>(ENDPOINTS.uploadDocument, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      },
    })
    return res
  },

  async list(params?: { skip?: number; limit?: number }): Promise<FinancialDocument[]> {
    const { data: res } = await apiClient.get<FinancialDocument[]>(ENDPOINTS.documents, { params })
    return res
  },

  async getById(id: number): Promise<FinancialDocument> {
    const { data: res } = await apiClient.get<FinancialDocument>(ENDPOINTS.document(id))
    return res
  },

  async delete(id: number): Promise<void> {
    await apiClient.delete(ENDPOINTS.document(id))
  },
}
