import { Box } from '@mui/material'
import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from '../Header/Header'
import { Sidebar } from '../Sidebar/Sidebar'
import { NotificationHost } from '../Notification/NotificationHost'

interface Props {
  children?: React.ReactNode
}

export function Layout({ children }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header onMenuClick={() => setSidebarOpen(true)} />
      <Box sx={{ display: 'flex', flex: 1, minHeight: 0 }}>
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <Box
          component="main"
          className="fade-in"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            p: { xs: 2, md: 3 },
            maxWidth: 1400,
            width: '100%',
            mx: 'auto',
            minHeight: 0,
          }}
        >
          {children ?? <Outlet />}
        </Box>
      </Box>
      <NotificationHost />
    </Box>
  )
}

export default Layout
