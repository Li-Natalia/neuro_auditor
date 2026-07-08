import { create } from 'zustand'
import { documentsApi } from '../../api/documentsApi'
import type { DocumentTemplate, FinancialDocument } from '../../types/document.types'
import { getErrorMessage } from '../../utils/helpers'

interface DocumentState {
  documents: FinancialDocument[]
  isLoading: boolean
  error: string | null
  uploadProgress: number
  fetchDocuments: () => Promise<void>
  upload: (file: File, template: DocumentTemplate) => Promise<FinancialDocument | undefined>
  remove: (id: number) => Promise<void>
  clearError: () => void
}

export const useDocumentStore = create<DocumentState>((set) => ({
  documents: [],
  isLoading: false,
  error: null,
  uploadProgress: 0,

  async fetchDocuments() {
    set({ isLoading: true, error: null })
    try {
      const docs = await documentsApi.list()
      set({ documents: docs, isLoading: false })
    } catch (e) {
      set({ isLoading: false, error: getErrorMessage(e) })
    }
  },

  async upload(file, template) {
    set({ uploadProgress: 0, error: null })
    try {
      const res = await documentsApi.upload({
        file,
        template,
        onProgress: (p) => set({ uploadProgress: p }),
      })
      set((s) => ({ documents: [res.document, ...s.documents], uploadProgress: 100 }))
      return res.document
    } catch (e) {
      set({ error: getErrorMessage(e), uploadProgress: 0 })
      throw e
    }
  },

  async remove(id) {
    try {
      await documentsApi.delete(id)
      set((s) => ({ documents: s.documents.filter((d) => d.id !== id) }))
    } catch (e) {
      set({ error: getErrorMessage(e) })
    }
  },

  clearError() {
    set({ error: null })
  },
}))
