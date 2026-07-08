import { useEffect, useState } from 'react'
import { Typography, Box, MenuItem, TextField, Grid } from '@mui/material'
import { AnalysisResults } from '../../components/analysis/AnalysisResults'
import { useAnalysis } from '../../hooks/useAnalysis'
import { useFileUpload } from '../../hooks/useFileUpload'
import LoadingSpinner from '../../components/common/LoadingSpinner/LoadingSpinner'

export function AnalysisPage() {
  const analysis = useAnalysis()
  const { documents, fetchDocuments } = useFileUpload()
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | ''>('')

  useEffect(() => {
    void fetchDocuments()
    void analysis.fetchList()
  }, [])

  const handleSelect = (id: number | '') => {
    setSelectedDocumentId(id)
    if (id !== '') {
      void analysis.fetchByDocument(Number(id))
    } else {
      analysis.clearError()
    }
  }

  const completedDocs = documents.filter((d) => d.analysisId)

  return (
    <>
      <Typography variant="h4" mb={2} className="gradient-text">
        Анализ отчетности
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <TextField
            select
            label="Выберите документ"
            value={selectedDocumentId}
            onChange={(e) => handleSelect(e.target.value === '' ? '' : Number(e.target.value))}
            fullWidth
          >
            <MenuItem value="">— не выбран —</MenuItem>
            {completedDocs.map((d) => (
              <MenuItem key={d.id} value={d.id}>
                {d.name}
              </MenuItem>
            ))}
          </TextField>
        </Grid>
      </Grid>

      <Box mt={3}>
        {analysis.isLoading ? (
          <LoadingSpinner message="Анализируем отчет..." />
        ) : (
          <AnalysisResults result={analysis.current} />
        )}
      </Box>
    </>
  )
}

export default AnalysisPage
