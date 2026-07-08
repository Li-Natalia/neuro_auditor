import { Box, LinearProgress, Typography } from '@mui/material'

interface Props {
  percent: number
  fileName?: string
}

export function UploadProgress({ percent, fileName }: Props) {
  return (
    <Box className="fade-in" sx={{ width: '100%' }}>
      <Box display="flex" justifyContent="space-between" mb={0.5}>
        <Typography variant="body2" color="text.secondary" noWrap>
          {fileName || 'Загрузка...'}
        </Typography>
        <Typography variant="body2" fontWeight={600}>
          {percent}%
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={percent}
        sx={{
          height: 10,
          borderRadius: 5,
          '& .MuiLinearProgress-bar': {
            background: 'linear-gradient(90deg,#2563EB,#7C3AED)',
          },
        }}
      />
    </Box>
  )
}

export default UploadProgress
