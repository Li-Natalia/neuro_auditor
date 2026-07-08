import { useState } from 'react'
import { Box, IconButton, TextField, InputAdornment } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'

interface Props {
  onSend: (text: string) => void
  disabled?: boolean
}

export function MessageInput({ onSend, disabled }: Props) {
  const [text, setText] = useState('')

  const submit = () => {
    if (!text.trim() || disabled) return
    onSend(text.trim())
    setText('')
  }

  return (
    <Box>
      <TextField
        fullWidth
        multiline
        maxRows={4}
        placeholder="Введите вопрос по отчетности..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            submit()
          }
        }}
        disabled={disabled}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton onClick={submit} disabled={disabled || !text.trim()} color="primary">
                <SendIcon />
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
    </Box>
  )
}

export default MessageInput
