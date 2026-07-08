import { useDocumentStore } from '../store/slices/documentSlice'

export function useFileUpload() {
  const store = useDocumentStore()
  return {
    documents: store.documents,
    isLoading: store.isLoading,
    error: store.error,
    uploadProgress: store.uploadProgress,
    upload: store.upload,
    fetchDocuments: store.fetchDocuments,
    remove: store.remove,
    clearError: store.clearError,
  }
}
