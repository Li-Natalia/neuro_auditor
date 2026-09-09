import { apiClient } from './client'
import { ENDPOINTS } from './endpoints'
import type { ChatCapabilities, ChatRequest, ChatResponse, ChatSession } from '../types/chat.types'

// Code Interpreter answers take minutes (the model runs code several times), so that request
// gets a longer timeout than the client's 30 s default (backend: AI_CI_TIMEOUT_SECONDS = 300 s).
const CODE_INTERPRETER_TIMEOUT_MS = 330_000

export const chatApi = {
  async ask(req: ChatRequest): Promise<ChatResponse> {
    const config = req.mode === 'code_interpreter' ? { timeout: CODE_INTERPRETER_TIMEOUT_MS } : undefined
    const { data: res } = await apiClient.post<ChatResponse>(ENDPOINTS.chat, req, config)
    return res
  },

  async getCapabilities(): Promise<ChatCapabilities> {
    const { data: res } = await apiClient.get<ChatCapabilities>(ENDPOINTS.chatCapabilities)
    return res
  },

  /** A Code Interpreter output file; the backend serves it only to the session owner. */
  async downloadArtifact(fileId: string): Promise<Blob> {
    const { data: res } = await apiClient.get<Blob>(ENDPOINTS.chatArtifact(fileId), {
      responseType: 'blob',
    })
    return res
  },

  async listSessions(): Promise<ChatSession[]> {
    const { data: res } = await apiClient.get<ChatSession[]>(ENDPOINTS.chatSessions)
    return res
  },

  async getSession(id: string): Promise<ChatSession> {
    const { data: res } = await apiClient.get<ChatSession>(ENDPOINTS.chatSession(id))
    return res
  },

  async deleteSession(id: string): Promise<void> {
    await apiClient.delete(ENDPOINTS.chatSession(id))
  },
}
