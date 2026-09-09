import { useChatStore } from '../store/slices/chatSlice'

export function useChat() {
  const store = useChatStore()
  return {
    sessions: store.sessions,
    activeSession: store.activeSession,
    isStreaming: store.isStreaming,
    error: store.error,
    mode: store.mode,
    codeInterpreterAvailable: store.codeInterpreterAvailable,
    fetchSessions: store.fetchSessions,
    fetchCapabilities: store.fetchCapabilities,
    setMode: store.setMode,
    startNewSession: store.startNewSession,
    selectSession: store.selectSession,
    sendMessage: store.sendMessage,
    downloadArtifact: store.downloadArtifact,
    clearError: store.clearError,
  }
}
