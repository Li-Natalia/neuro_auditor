import { Box, Button, Typography } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import HomeIcon from '@mui/icons-material/Home'

export default function NotFound() {
  const navigate = useNavigate()
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height="100vh"
      gap={2}
    >
      <Typography variant="h1" className="gradient-text" fontWeight={800}>
        404
      </Typography>
      <Typography variant="h6" color="text.secondary">
        Страница не найдена
      </Typography>
      <Button variant="contained" startIcon={<HomeIcon />} onClick={() => navigate('/')}>
        На главную
      </Button>
    </Box>
  )
}
