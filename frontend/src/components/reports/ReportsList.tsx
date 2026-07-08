import { Grid, Box, Typography } from '@mui/material'
import type { FinancialDocument } from '../../types/document.types'
import { ReportCard } from './ReportCard'

interface Props {
  documents: FinancialDocument[]
  onDelete?: (id: number) => void
}

export function ReportsList({ documents, onDelete }: Props) {
  if (documents.length === 0) {
    return (
      <Box textAlign="center" py={6}>
        <Typography variant="h6" color="text.secondary">
          Нет загруженных отчётов
        </Typography>
        <Typography color="text.secondary">Загрузите первый Excel-файл на странице «Загрузка».</Typography>
      </Box>
    )
  }

  return (
    <Grid container spacing={2}>
      {documents.map((doc) => (
        <Grid item xs={12} sm={6} md={4} key={doc.id}>
          <ReportCard document={doc} onDelete={onDelete} />
        </Grid>
      ))}
    </Grid>
  )
}

export default ReportsList
