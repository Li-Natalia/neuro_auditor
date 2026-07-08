import { useState, useMemo } from 'react'
import { Grid, Box, Typography, Alert } from '@mui/material'
import type { AnalysisResult, Risk } from '../../types/analysis.types'
import { FinancialCharts } from './FinancialCharts'
import { ReportDetails } from './ReportDetails'
import { RiskCard } from './RiskCard'
import { RiskFilters } from './RiskFilters'

interface Props {
  result: AnalysisResult | null
}

export function AnalysisResults({ result }: Props) {
  const [filteredRisks, setFilteredRisks] = useState<Risk[] | null>(null)

  const risks = useMemo(() => filteredRisks ?? result?.risks ?? [], [filteredRisks, result])

  if (!result) {
    return (
      <Alert severity="info" sx={{ borderRadius: 2 }}>
        Выберите документ, чтобы увидеть результаты анализа.
      </Alert>
    )
  }

  return (
    <Box className="fade-in" display="flex" flexDirection="column" gap={2}>
      <FinancialCharts result={result} />
      <ReportDetails result={result} />

      <Box>
        <Typography variant="h6" mb={1}>Выявленные риски</Typography>
        <RiskFilters risks={result.risks} onFilter={setFilteredRisks} />
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {risks.length === 0 && (
            <Typography color="text.secondary" sx={{ p: 2 }}>
              Риски не выявлены
            </Typography>
          )}
          {risks.map((risk) => (
            <Grid item xs={12} md={6} key={risk.id}>
              <RiskCard risk={risk} />
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  )
}

export default AnalysisResults
