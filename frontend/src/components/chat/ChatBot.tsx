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
  const { documents } = useFileUpload()
  const [documentId, setDocumentId] = useState<number | undefined>(undefined)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chat.fetchSessions()
    if (!chat.activeSession) chat.startNewSession()
  }, [])

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

        <DocumentContext documents={documents} value={documentId} onChange={setDocumentId} />
        <Divider />

        <MessageList
          messages={chat.activeSession?.messages ?? []}
          isStreaming={chat.isStreaming}
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
