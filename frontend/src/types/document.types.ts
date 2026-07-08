export type DocumentTemplate = 'IFRS' | 'RSBU'
export type DocumentStatus = 'uploaded' | 'processing' | 'completed' | 'failed'

export interface FinancialDocument {
  id: number
  name: string
  template: DocumentTemplate
  status: DocumentStatus
  fileSize: number
  uploadedAt: string
  processingProgress?: number
  uploadedById: number
  analysisId?: number | null
}

export interface UploadResponse {
  document: FinancialDocument
  message: string
}
