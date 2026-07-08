import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Button,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import type { FinancialDocument } from '../../types/document.types'
import { formatShortDate, bytesToMB } from '../../utils/formatters'

interface Props {
  documents: FinancialDocument[]
}

const STATUS_LABELS: Record<string, { label: string; color: 'default' | 'warning' | 'success' | 'error' }> = {
  uploaded: { label: 'Загружен', color: 'default' },
  processing: { label: 'Обработка', color: 'warning' },
  completed: { label: 'Готов', color: 'success' },
  failed: { label: 'Ошибка', color: 'error' },
}

export function RecentReports({ documents }: Props) {
  const navigate = useNavigate()
  const recent = documents.slice(0, 5)

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
          <Typography variant="h6">Последние отчёты</Typography>
          <Button size="small" onClick={() => navigate('/reports')}>
            Все отчёты
          </Button>
        </Box>
        <List>
          {recent.length === 0 && (
            <Typography color="text.secondary" py={2} align="center">
              Пока нет загруженных отчётов
            </Typography>
          )}
          {recent.map((doc) => {
            const status = STATUS_LABELS[doc.status] ?? STATUS_LABELS.uploaded
            return (
              <ListItem
                key={doc.id}
                sx={{
                  borderRadius: 2,
                  '&:hover': { bgcolor: 'action.hover' },
                  cursor: 'pointer',
                }}
                onClick={() => navigate(`/analysis`)}
              >
                <ListItemText
                  primary={doc.name}
                  secondary={`${doc.template} • ${bytesToMB(doc.fileSize)} • ${formatShortDate(doc.uploadedAt)}`}
                />
                <Chip size="small" label={status.label} color={status.color} />
              </ListItem>
            )
          })}
        </List>
      </CardContent>
    </Card>
  )
}

export default RecentReports
