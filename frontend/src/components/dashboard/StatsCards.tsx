import { Grid, Card, CardContent, Typography, Box } from '@mui/material'
import FolderIcon from '@mui/icons-material/Folder'
import WarningIcon from '@mui/icons-material/Warning'
import ErrorIcon from '@mui/icons-material/Error'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import type { AnalysisSummary } from '../../types/analysis.types'

interface Props {
  summary: AnalysisSummary | null
}

const CARDS = [
  { key: 'totalDocuments', label: 'Отчётов', icon: FolderIcon, color: '#2563EB' },
  { key: 'totalRisks', label: 'Всего рисков', icon: WarningIcon, color: '#F59E0B' },
  { key: 'criticalRisks', label: 'Критических', icon: ErrorIcon, color: '#EF4444' },
  { key: 'averageRiskScore', label: 'Ср. оценка риска', icon: TrendingUpIcon, color: '#10B981' },
] as const

export function StatsCards({ summary }: Props) {
  return (
    <Grid container spacing={2}>
      {CARDS.map((card) => {
        const Icon = card.icon
        const value =
          summary ? (summary as any)[card.key] ?? 0 : 0
        return (
          <Grid item xs={12} sm={6} md={3} key={card.key}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      {card.label}
                    </Typography>
                    <Typography variant="h4" fontWeight={700}>
                      {card.key === 'averageRiskScore'
                        ? Number(value).toFixed(1)
                        : value}
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 3,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `${card.color}22`,
                      color: card.color,
                    }}
                  >
                    <Icon />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )
      })}
    </Grid>
  )
}

export default StatsCards
