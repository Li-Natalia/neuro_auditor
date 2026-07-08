import { Chip, Box, Typography } from '@mui/material'
import { SUGGESTED_QUESTIONS } from '../../types/chat.types'

interface Props {
  onSelect: (question: string) => void
}

export function SuggestedQuestions({ onSelect }: Props) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" mb={1} display="block">
        Предложенные вопросы:
      </Typography>
      <Box display="flex" flexWrap="wrap" gap={1}>
        {SUGGESTED_QUESTIONS.map((q) => (
          <Chip
            key={q}
            label={q}
            variant="outlined"
            onClick={() => onSelect(q)}
            sx={{ borderRadius: 2, '&:hover': { bgcolor: 'action.hover' } }}
          />
        ))}
      </Box>
    </Box>
  )
}

export default SuggestedQuestions
