export type MessageRole = 'user' | 'assistant' | 'system'

/**
 * How the chat should answer:
 * - 'auto' — fast answer from the document's computed figures, unless the question asks for a
 *   file / table / chart or a recalculation "по файлу" (then Code Interpreter runs on the workbook);
 * - 'context' — always the fast path;
 * - 'code_interpreter' — always run code on the uploaded workbook (needs a document).
 */
export type ChatMode = 'auto' | 'context' | 'code_interpreter'

/** The mode the backend actually answered in. */
export type AnsweredMode = 'context' | 'code_interpreter'

/** A file the model produced in Code Interpreter mode; downloadable via chatApi.downloadArtifact. */
export interface ChatArtifact {
  fileId: string
  filename: string
}

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  createdAt: string
  mode?: AnsweredMode
  artifacts?: ChatArtifact[]
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
  mode?: ChatMode
}

export interface ChatResponse {
  answer: string
  sources?: string[]
  sessionId: string
  mode?: AnsweredMode
  artifacts?: ChatArtifact[]
}

export interface ChatCapabilities {
  codeInterpreter: boolean
}

export const SUGGESTED_QUESTIONS = [
  'Как изменилась выручка за последний год?',
  'Какие риски выявлены в отчетности?',
  'Сравни показатели ликвидности с нормативами',
  'Оцени вероятность банкротства по отчетности',
  'Какова динамика чистой прибыли?',
] as const
