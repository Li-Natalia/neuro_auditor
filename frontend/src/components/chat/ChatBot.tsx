import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, Box, Typography, Divider, Button } from '@mui/material'
import AddCommentIcon from '@mui/icons-material/AddComment'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { SuggestedQuestions } from './SuggestedQuestions'
import { DocumentContext } from './DocumentContext'
import { useChat } from '../../hooks/useChat'
import { useFileUpload } from '../../hooks/useFileUpload'

export function ChatBot() {
  const chat = useChat()
  const { documents, fetchDocuments } = useFileUpload()
  const [documentId, setDocumentId] = useState<number | undefined>(undefined)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Load documents too, so the context selector is populated on a direct
    // refresh of /chat (they're otherwise fetched only on the upload page).
    fetchDocuments()
    chat.fetchSessions()
    chat.fetchCapabilities()
    if (!chat.activeSession) chat.startNewSession()
  }, [])

  // "Расчёт по файлу" needs a document, so drop back to auto as soon as the
  // selection is cleared.
  const { mode, setMode } = chat
  useEffect(() => {
    if (documentId === undefined && mode === 'code_interpreter') setMode('auto')
  }, [documentId, mode, setMode])

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chat.activeSession?.messages, chat.isStreaming])

  const handleSend = (text: string) => {
    void chat.sendMessage(text, documentId)
  }

  return (
    <Card sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 1, overflow: 'hidden' }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Чат-бот по документам</Typography>
          <Button
            size="small"
            startIcon={<AddCommentIcon />}
            onClick={() => chat.startNewSession(documentId)}
          >
            Новая сессия
          </Button>
        </Box>

        <DocumentContext
          documents={documents}
          value={documentId}
          onChange={setDocumentId}
          mode={mode}
          onModeChange={setMode}
          codeInterpreterAvailable={chat.codeInterpreterAvailable}
        />
        <Divider />

        <MessageList
          messages={chat.activeSession?.messages ?? []}
          isStreaming={chat.isStreaming}
          onDownloadArtifact={chat.downloadArtifact}
        />

        {chat.activeSession && chat.activeSession.messages.length === 0 && (
          <SuggestedQuestions onSelect={handleSend} />
        )}

        <MessageInput onSend={handleSend} disabled={chat.isStreaming} />
        <div ref={scrollRef} />
      </CardContent>
    </Card>
  )
}

export default ChatBot
