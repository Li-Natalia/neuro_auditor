import { create } from 'zustand'
import { chatApi } from '../../api/chatApi'
import type { ChatArtifact, ChatMessage, ChatMode, ChatSession } from '../../types/chat.types'
import { downloadBlob, getErrorMessage } from '../../utils/helpers'

function makeId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

interface ChatState {
  sessions: ChatSession[]
  activeSession: ChatSession | null
  isStreaming: boolean
  error: string | null
  mode: ChatMode
  codeInterpreterAvailable: boolean
  fetchSessions: () => Promise<void>
  fetchCapabilities: () => Promise<void>
  setMode: (mode: ChatMode) => void
  startNewSession: (documentId?: number) => void
  selectSession: (id: string) => void
  sendMessage: (content: string, documentId?: number) => Promise<void>
  downloadArtifact: (artifact: ChatArtifact) => Promise<void>
  clearError: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSession: null,
  isStreaming: false,
  error: null,
  mode: 'auto',
  codeInterpreterAvailable: false,

  async fetchSessions() {
    try {
      const sessions = await chatApi.listSessions()
      set({ sessions })
    } catch (e) {
      set({ error: getErrorMessage(e) })
    }
  },

  async fetchCapabilities() {
    try {
      const caps = await chatApi.getCapabilities()
      set({ codeInterpreterAvailable: caps.codeInterpreter === true })
    } catch {
      // Best-effort probe: if it fails the mode toggle stays hidden and every
      // request keeps going out in plain "context" mode.
      set({ codeInterpreterAvailable: false })
    }
  },

  setMode(mode) {
    set({ mode })
  },

  startNewSession(documentId) {
    const session: ChatSession = {
      id: makeId(),
      title: 'Новая сессия',
      documentId,
      createdAt: new Date().toISOString(),
      messages: [],
    }
    set({ activeSession: session })
  },

  selectSession(id) {
    const session = get().sessions.find((s) => s.id === id) || null
    set({ activeSession: session })
  },

  async sendMessage(content, documentId) {
    if (!content.trim()) return
    set({ isStreaming: true, error: null })

    let session = get().activeSession
    if (!session) {
      session = {
        id: makeId(),
        title: content.slice(0, 40),
        documentId,
        createdAt: new Date().toISOString(),
        messages: [],
      }
      set({ activeSession: session })
    }

    const userMsg: ChatMessage = {
      id: makeId(),
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    }
    set((s) => ({
      activeSession: s.activeSession
        ? { ...s.activeSession, messages: [...s.activeSession.messages, userMsg] }
        : s.activeSession,
    }))

    // Code Interpreter (the target of "auto" routing too) needs the capability and a
    // document — the backend answers 422 otherwise — so without them use the fast path.
    const { mode: selectedMode, codeInterpreterAvailable } = get()
    const mode: ChatMode =
      codeInterpreterAvailable && documentId !== undefined ? selectedMode : 'context'

    try {
      const res = await chatApi.ask({ message: content, documentId, sessionId: session.id, mode })
      const artifacts = res.artifacts ?? []
      const assistantMsg: ChatMessage = {
        id: makeId(),
        role: 'assistant',
        content: res.answer,
        createdAt: new Date().toISOString(),
        mode: res.mode,
        // Code Interpreter outputs: rendered as download buttons under the answer.
        artifacts: artifacts.length > 0 ? artifacts : undefined,
      }
      set((s) => ({
        activeSession: s.activeSession
          ? {
              ...s.activeSession,
              id: res.sessionId || s.activeSession.id,
              messages: [...s.activeSession.messages, assistantMsg],
            }
          : s.activeSession,
        isStreaming: false,
      }))
    } catch (e) {
      set({ isStreaming: false, error: getErrorMessage(e) })
    }
  },

  async downloadArtifact(artifact) {
    try {
      const blob = await chatApi.downloadArtifact(artifact.fileId)
      downloadBlob(blob, artifact.filename)
    } catch (e) {
      set({ error: getErrorMessage(e, 'Не удалось скачать файл') })
    }
  },

  clearError() {
    set({ error: null })
  },
}))
