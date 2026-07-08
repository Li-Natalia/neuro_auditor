import { apiClient } from './client'
import { ENDPOINTS } from './endpoints'
import type { ChatRequest, ChatResponse, ChatSession } from '../types/chat.types'

export const chatApi = {
  async ask(req: ChatRequest): Promise<ChatResponse> {
    const { data: res } = await apiClient.post<ChatResponse>(ENDPOINTS.chat, req)
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
