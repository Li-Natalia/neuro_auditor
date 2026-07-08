import { Box, CircularProgress, Typography } from '@mui/material'

interface Props {
  size?: number
  message?: string
  fullScreen?: boolean
}

export function LoadingSpinner({ size = 40, message, fullScreen }: Props) {
  const content = (
    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" gap={2}>
      <CircularProgress size={size} />
      {message && <Typography color="text.secondary">{message}</Typography>}
    </Box>
  )
  if (fullScreen) {
    return (
      <Box display="flex" alignItems="center" justifyContent="center" height="100vh" width="100%">
        {content}
      </Box>
    )
  }
  return <Box display="flex" justifyContent="center" p={4}>{content}</Box>
}

export default LoadingSpinner
