import { Typography, Box } from '@mui/material'
import { ChatBot } from '../../components/chat/ChatBot'

export function ChatPage() {
  return (
    <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
      <Typography variant="h4" mb={2} className="gradient-text">
        Чат-бот
      </Typography>
      <ChatBot />
    </Box>
  )
}

export default ChatPage
