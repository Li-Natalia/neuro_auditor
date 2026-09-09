import {
  MenuItem,
  TextField,
  Typography,
  Box,
  ToggleButtonGroup,
  ToggleButton,
  Tooltip,
} from '@mui/material'
import type { FinancialDocument } from '../../types/document.types'
import type { ChatMode } from '../../types/chat.types'

interface Props {
  documents: FinancialDocument[]
  value?: number
  onChange: (id: number | undefined) => void
  mode: ChatMode
  onModeChange: (mode: ChatMode) => void
  codeInterpreterAvailable: boolean
}

const MODE_HINTS: Record<ChatMode, string> = {
  auto:
    'Быстрый ответ по рассчитанным показателям. Если попросить файл, таблицу, график или пересчёт по файлу, модель выполнит код по отчёту (1–3 минуты).',
  context: 'Ответ по уже рассчитанным показателям и рискам документа, без выполнения кода.',
  code_interpreter:
    'Модель выполняет код по файлу отчёта (Code Interpreter), ответ может занять 1–3 минуты.',
}

export function DocumentContext({
  documents,
  value,
  onChange,
  mode,
  onModeChange,
  codeInterpreterAvailable,
}: Props) {
  const hasDocument = value !== undefined

  return (
    <Box>
      <Typography variant="caption" color="text.secondary">Контекст документа:</Typography>
      <TextField
        select
        size="small"
        fullWidth
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : undefined)}
        SelectProps={{ displayEmpty: true }}
        sx={{ mt: 0.5 }}
      >
        <MenuItem value="">Без контекста</MenuItem>
        {documents.map((d) => (
          <MenuItem key={d.id} value={d.id}>
            {d.name}
          </MenuItem>
        ))}
      </TextField>

      {codeInterpreterAvailable && (
        <>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            Режим ответа:
          </Typography>
          <ToggleButtonGroup
            exclusive
            size="small"
            value={mode}
            onChange={(_e, next: ChatMode | null) => {
              // Re-clicking the selected button yields null; keep the current mode.
              if (next) onModeChange(next)
            }}
            sx={{ mt: 0.5 }}
          >
            <ToggleButton value="auto">Авто</ToggleButton>
            <ToggleButton value="context">Быстрый ответ</ToggleButton>
            {/* A disabled button emits no pointer events, so the Tooltip needs a wrapper. */}
            <Tooltip title={hasDocument ? '' : 'Выберите документ'}>
              <Box component="span" sx={{ display: 'inline-flex' }}>
                <ToggleButton value="code_interpreter" disabled={!hasDocument}>
                  Расчёт по файлу
                </ToggleButton>
              </Box>
            </Tooltip>
          </ToggleButtonGroup>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
            {MODE_HINTS[mode]}
          </Typography>
        </>
      )}
    </Box>
  )
}

export default DocumentContext
