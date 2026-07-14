import { create } from 'zustand'
import { chatApi } from '../../api/chatApi'
import type { ChatMessage, ChatSession } from '../../types/chat.types'
import { getErrorMessage } from '../../utils/helpers'

function makeId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

interface ChatState {
  sessions: ChatSession[]
  activeSession: ChatSession | null
  isStreaming: boolean
  error: string | null
  fetchSessions: () => Promise<void>
  startNewSession: (documentId?: number) => void
  selectSession: (id: string) => void
  sendMessage: (content: string, documentId?: number) => Promise<void>
  clearError: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSession: null,
  isStreaming: false,
  error: null,

  async fetchSessions() {
    try {
      const sessions = await chatApi.listSessions()
      set({ sessions })
    } catch (e) {
      set({ error: getErrorMessage(e) })
    }
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

    try {
      const res = await chatApi.ask({ message: content, documentId, sessionId: session.id })
      const assistantMsg: ChatMessage = {
        id: makeId(),
        role: 'assistant',
        content: res.answer,
        createdAt: new Date().toISOString(),
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

  clearError() {
    set({ error: null })
  },
}))
