export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  createdAt: string
}

export interface ChatSession {
  id: string
  title: string
  documentId?: number
  createdAt: string
  messages: ChatMessage[]
}

export interface ChatRequest {
  message: string
  documentId?: number
  sessionId?: string
}

export interface ChatResponse {
  answer: string
  sources?: string[]
  sessionId: string
}

export const SUGGESTED_QUESTIONS = [
  'Как изменилась выручка за последний год?',
  'Какие риски выявлены в отчетности?',
  'Сравни показатели ликвидности с нормативами',
  'Оцени вероятность банкротства по отчетности',
  'Какова динамика чистой прибыли?',
] as const
