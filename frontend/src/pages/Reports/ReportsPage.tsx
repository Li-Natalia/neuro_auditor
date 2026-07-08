import { useEffect } from 'react'
import { Typography } from '@mui/material'
import { ReportsList } from '../../components/reports/ReportsList'
import { useFileUpload } from '../../hooks/useFileUpload'

export function ReportsPage() {
  const { documents, fetchDocuments, remove } = useFileUpload()

  useEffect(() => {
    void fetchDocuments()
  }, [])

  return (
    <>
      <Typography variant="h4" mb={2} className="gradient-text">
        История отчётов
      </Typography>
      <ReportsList documents={documents} onDelete={remove} />
    </>
  )
}

export default ReportsPage
