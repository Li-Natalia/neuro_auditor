import { Card, CardContent, Box, Typography, Chip, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import DescriptionIcon from '@mui/icons-material/Description'
import type { FinancialDocument } from '../../types/document.types'
import { formatShortDate, bytesToMB } from '../../utils/formatters'

interface Props {
  document: FinancialDocument
  onDelete?: (id: number) => void
}

const STATUS_COLOR: Record<string, 'default' | 'warning' | 'success' | 'error'> = {
  uploaded: 'default',
  processing: 'warning',
  completed: 'success',
  failed: 'error',
}

export function ReportCard({ document: doc, onDelete }: Props) {
  const navigate = useNavigate()
  return (
    <Card
      sx={{
        height: '100%',
        transition: 'all 0.2s ease',
        '&:hover': { transform: 'translateY(-2px)', boxShadow: 6 },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" gap={1.5}>
          <DescriptionIcon color="primary" />
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography variant="subtitle1" fontWeight={600} noWrap>
              {doc.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {doc.template} • {bytesToMB(doc.fileSize)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {formatShortDate(doc.uploadedAt)}
            </Typography>
          </Box>
          <Chip
            size="small"
            label={doc.status}
            color={STATUS_COLOR[doc.status] ?? 'default'}
          />
        </Box>
        <Box display="flex" gap={1} mt={2}>
          <Button
            size="small"
            variant="outlined"
            onClick={() => navigate('/analysis')}
          >
            Открыть
          </Button>
          {onDelete && (
            <Button
              size="small"
              color="error"
              variant="text"
              onClick={() => onDelete(doc.id)}
            >
              Удалить
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  )
}

export default ReportCard
