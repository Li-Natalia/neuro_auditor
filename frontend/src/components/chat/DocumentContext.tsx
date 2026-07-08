import { MenuItem, TextField, Typography, Box } from '@mui/material'
import type { FinancialDocument } from '../../types/document.types'

interface Props {
  documents: FinancialDocument[]
  value?: number
  onChange: (id: number | undefined) => void
}

export function DocumentContext({ documents, value, onChange }: Props) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary">Контекст документа:</Typography>
      <TextField
        select
        size="small"
        fullWidth
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
        sx={{ mt: 0.5 }}
      >
        <MenuItem value="">Без контекста</MenuItem>
        {documents.map((d) => (
          <MenuItem key={d.id} value={d.id}>
            {d.name}
          </MenuItem>
        ))}
      </TextField>
    </Box>
  )
}

export default DocumentContext
