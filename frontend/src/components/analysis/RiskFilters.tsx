import { Box, ToggleButtonGroup, ToggleButton, Typography } from '@mui/material'
import { useState } from 'react'
import type { Risk } from '../../types/analysis.types'
import type { RiskLevel } from '../../utils/constants'

interface Props {
  risks: Risk[]
  onFilter: (filtered: Risk[]) => void
}

type Filter = 'all' | RiskLevel

export function RiskFilters({ risks, onFilter }: Props) {
  const [filter, setFilter] = useState<Filter>('all')

  const handleFilter = (_: unknown, value: Filter | null) => {
    const next = value ?? 'all'
    setFilter(next)
    if (next === 'all') {
      onFilter(risks)
    } else {
      onFilter(risks.filter((r) => r.level === next))
    }
  }

  return (
    <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
      <Typography variant="body2" color="text.secondary">
        Фильтр рисков:
      </Typography>
      <ToggleButtonGroup
        value={filter}
        exclusive
        onChange={handleFilter}
        size="small"
      >
        <ToggleButton value="all">Все</ToggleButton>
        <ToggleButton value="critical">🔴 Критические</ToggleButton>
        <ToggleButton value="medium">🟡 Средние</ToggleButton>
        <ToggleButton value="low">🟢 Низкие</ToggleButton>
      </ToggleButtonGroup>
    </Box>
  )
}

export default RiskFilters
