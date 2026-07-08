import { Box, Typography, Avatar, Paper } from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import PersonIcon from '@mui/icons-material/Person'
import type { ChatMessage } from '../../types/chat.types'
import { formatDate } from '../../utils/formatters'

interface Props {
  messages: ChatMessage[]
  isStreaming: boolean
}

export function MessageList({ messages, isStreaming }: Props) {
  if (messages.length === 0) {
    return (
      <Box flex={1} display="flex" alignItems="center" justifyContent="center">
        <Typography color="text.secondary">
          Задайте вопрос по загруженным отчётам
        </Typography>
      </Box>
    )
  }
  return (
    <Box flex={1} sx={{ overflowY: 'auto', px: 1, py: 2 }}>
      {messages.map((msg) => {
        const isUser = msg.role === 'user'
        return (
          <Box
            key={msg.id}
            display="flex"
            justifyContent={isUser ? 'flex-end' : 'flex-start'}
            mb={1.5}
          >
            {!isUser && (
              <Avatar sx={{ width: 32, height: 32, mr: 1, bgcolor: 'secondary.main' }}>
                <SmartToyIcon fontSize="small" />
              </Avatar>
            )}
            <Paper
              sx={{
                maxWidth: '70%',
                px: 2,
                py: 1.5,
                borderRadius: 3,
                bgcolor: isUser
                  ? 'linear-gradient(135deg,#2563EB,#7C3AED)'
                  : 'background.paper',
                background: isUser ? 'linear-gradient(135deg,#2563EB,#7C3AED)' : undefined,
                color: isUser ? '#fff' : 'text.primary',
                boxShadow: 1,
              }}
            >
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {msg.content}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mt: 0.5 }}>
                {formatDate(msg.createdAt)}
              </Typography>
            </Paper>
            {isUser && (
              <Avatar sx={{ width: 32, height: 32, ml: 1, bgcolor: 'primary.main' }}>
                <PersonIcon fontSize="small" />
              </Avatar>
            )}
          </Box>
        )
      })}
      {isStreaming && (
        <Box display="flex" gap={1} px={1}>
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
            <SmartToyIcon fontSize="small" />
          </Avatar>
          <Typography color="text.secondary" sx={{ alignSelf: 'center' }}>
            печатает...
          </Typography>
        </Box>
      )}
    </Box>
  )
}

export default MessageList
