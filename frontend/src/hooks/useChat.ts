import { useChatStore } from '../store/slices/chatSlice'

export function useChat() {
  const store = useChatStore()
  return {
    sessions: store.sessions,
    activeSession: store.activeSession,
    isStreaming: store.isStreaming,
    error: store.error,
    fetchSessions: store.fetchSessions,
    startNewSession: store.startNewSession,
    selectSession: store.selectSession,
    sendMessage: store.sendMessage,
    clearError: store.clearError,
  }
}
