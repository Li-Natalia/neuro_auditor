import { Typography } from '@mui/material'
import { FileUpload } from '../../components/upload/FileUpload'

export function UploadPage() {
  return (
    <>
      <Typography variant="h4" mb={2} className="gradient-text">
        Загрузка отчётов
      </Typography>
      <FileUpload />
    </>
  )
}

export default UploadPage
