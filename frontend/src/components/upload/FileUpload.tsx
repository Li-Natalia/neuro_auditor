import { useState } from 'react'
import { Card, CardContent, Box, MenuItem, TextField, Button, Typography } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { DragAndDropZone } from './DragAndDropZone'
import { UploadProgress } from './UploadProgress'
import { useFileUpload } from '../../hooks/useFileUpload'
import { useThemeStore } from '../../store/slices/uiSlice'
import { REPORT_TEMPLATES } from '../../utils/constants'
import type { DocumentTemplate } from '../../types/document.types'

export function FileUpload() {
  const navigate = useNavigate()
  const { upload, uploadProgress } = useFileUpload()
  const { notify } = useThemeStore()
  const [template, setTemplate] = useState<DocumentTemplate>('RSBU')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleSubmit = async () => {
    if (!selectedFile) return
    setIsUploading(true)
    try {
      const doc = await upload(selectedFile, template)
      notify(`Файл «${doc?.name}» загружен`, 'success')
      setSelectedFile(null)
      navigate('/analysis')
    } catch {
      notify('Не удалось загрузить файл', 'error')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" flexDirection="column" gap={2}>
          <Typography variant="h6">Загрузка финансовой отчетности</Typography>
          <TextField
            select
            label="Шаблон отчетности"
            value={template}
            onChange={(e) => setTemplate(e.target.value as DocumentTemplate)}
            fullWidth
            size="small"
          >
            {REPORT_TEMPLATES.map((t) => (
              <MenuItem key={t.value} value={t.value}>
                {t.label}
              </MenuItem>
            ))}
          </TextField>

          <DragAndDropZone
            disabled={isUploading}
            onFileSelected={(file) => setSelectedFile(file)}
          />

          {selectedFile && !isUploading && (
            <Typography variant="body2">Выбран файл: {selectedFile.name}</Typography>
          )}

          {isUploading && (
            <UploadProgress percent={uploadProgress} fileName={selectedFile?.name} />
          )}

          <Box display="flex" justifyContent="flex-end" gap={1}>
            <Button disabled={!selectedFile || isUploading} onClick={() => setSelectedFile(null)}>
              Очистить
            </Button>
            <Button
              variant="contained"
              disabled={!selectedFile || isUploading}
              onClick={handleSubmit}
            >
              Загрузить и проанализировать
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

export default FileUpload
