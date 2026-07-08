import { Card, CardContent, Box, Typography, Chip } from '@mui/material'
import type { Risk } from '../../types/analysis.types'
import { RISK_META } from '../../utils/constants'

interface Props {
  risk: Risk
}

const EMOJI: Record<string, string> = { critical: '🔴', medium: '🟡', low: '🟢' }

export function RiskCard({ risk }: Props) {
  const meta = RISK_META[risk.level]
  return (
    <Card
      sx={{
        borderLeft: `4px solid ${meta.color}`,
        height: '100%',
        transition: 'transform 0.2s ease',
        '&:hover': { transform: 'translateY(-2px)' },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          <span>{EMOJI[risk.level]}</span>
          <Typography variant="subtitle1" fontWeight={600} sx={{ flex: 1 }}>
            {risk.title}
          </Typography>
          <Chip
            label={meta.label}
            size="small"
            sx={{ bgcolor: `${meta.color}22`, color: meta.color, fontWeight: 600 }}
          />
        </Box>
        <Typography variant="body2" color="text.secondary" mb={1}>
          {risk.description}
        </Typography>
        {risk.metric && (
          <Typography variant="caption" color="text.secondary" display="block" mb={1}>
            Показатель: {risk.metric} = {risk.value ?? '—'}
            {risk.threshold !== undefined ? ` (норма: ${risk.threshold})` : ''}
          </Typography>
        )}
        <Box
          sx={{
            p: 1,
            borderRadius: 2,
            bgcolor: 'action.hover',
          }}
        >
          <Typography variant="body2">
            <strong>Рекомендация:</strong> {risk.recommendation}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

export default RiskCard
