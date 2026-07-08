import { useCallback, useState } from 'react'
import { Box, Typography, Paper } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile'
import { ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_SIZE_MB } from '../../utils/constants'

interface Props {
  onFileSelected: (file: File) => void
  disabled?: boolean
}

export function DragAndDropZone({ onFileSelected, disabled }: Props) {
  const [isDragging, setIsDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validate = useCallback((file: File): string | null => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!ext || !ALLOWED_UPLOAD_EXTENSIONS.includes(ext as any)) {
      return 'Допустимы только файлы .xlsx и .xls'
    }
    if (file.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024) {
      return `Максимальный размер файла — ${MAX_UPLOAD_SIZE_MB} МБ`
    }
    return null
  }, [])

  const handleFile = useCallback(
    (file: File) => {
      const err = validate(file)
      if (err) {
        setError(err)
        return
      }
      setError(null)
      onFileSelected(file)
    },
    [onFileSelected, validate],
  )

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (disabled) return
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <Paper
      variant="outlined"
      onDragOver={(e) => {
        e.preventDefault()
        if (!disabled) setIsDragging(true)
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      sx={{
        borderStyle: 'dashed',
        borderWidth: 2,
        borderColor: isDragging ? 'primary.main' : 'divider',
        bgcolor: isDragging ? 'rgba(37,99,235,0.04)' : 'background.paper',
        p: 5,
        textAlign: 'center',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.2s ease',
        '&:hover': { borderColor: 'primary.light', bgcolor: 'rgba(37,99,235,0.03)' },
      }}
      onClick={() => document.getElementById('file-input')?.click()}
    >
      <input
        id="file-input"
        type="file"
        hidden
        accept=".xlsx,.xls"
        onChange={handleChange}
      />
      <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
        {isDragging ? (
          <InsertDriveFileIcon color="primary" sx={{ fontSize: 56 }} />
        ) : (
          <CloudUploadIcon color="primary" sx={{ fontSize: 56 }} />
        )}
        <Typography variant="h6">Перетащите Excel-файл сюда</Typography>
        <Typography variant="body2" color="text.secondary">
          или нажмите для выбора. Поддерживаются .xlsx, .xls (до {MAX_UPLOAD_SIZE_MB} МБ)
        </Typography>
        {error && (
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        )}
      </Box>
    </Paper>
  )
}

export default DragAndDropZone
