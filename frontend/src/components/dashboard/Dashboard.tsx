import { Box, Grid } from '@mui/material'
import { useEffect } from 'react'
import { StatsCards } from './StatsCards'
import { RecentReports } from './RecentReports'
import { useAnalysis } from '../../hooks/useAnalysis'
import { useFileUpload } from '../../hooks/useFileUpload'

export function Dashboard() {
  const { summary, fetchSummary } = useAnalysis()
  const { documents, fetchDocuments } = useFileUpload()

  useEffect(() => {
    void fetchSummary()
    void fetchDocuments()
  }, [fetchSummary, fetchDocuments])

  return (
    <Box className="fade-in" display="flex" flexDirection="column" gap={2}>
      <StatsCards summary={summary} />
      <Grid container spacing={2}>
        <Grid item xs={12} md={7}>
          <RecentReports documents={documents} />
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
