import { AppBar, Toolbar, Typography, IconButton, Avatar, Menu, MenuItem, Box, Tooltip } from '@mui/material'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MenuIcon from '@mui/icons-material/Menu'
import Brightness4Icon from '@mui/icons-material/Brightness4'
import Brightness7Icon from '@mui/icons-material/Brightness7'
import LogoutIcon from '@mui/icons-material/Logout'
import { useThemeStore } from '../../../store/slices/uiSlice'
import { useAuthStore } from '../../../store/slices/authSlice'
import { APP_NAME } from '../../../utils/constants'

interface Props {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: Props) {
  const navigate = useNavigate()
  const { mode, toggleTheme } = useThemeStore()
  const { user, logout } = useAuthStore()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  const initials = user?.name
    ? user.name.split(' ').map((p) => p[0]).slice(0, 2).join('').toUpperCase()
    : '?'

  return (
    <AppBar
      position="sticky"
      sx={{
        backdropFilter: 'blur(8px)',
        backgroundColor: (t) => (t.palette.mode === 'dark' ? 'rgba(30,41,59,0.7)' : 'rgba(255,255,255,0.7)'),
        borderBottom: (t) => `1px solid ${t.palette.divider}`,
      }}
    >
      <Toolbar sx={{ gap: 1 }}>
        <IconButton edge="start" onClick={onMenuClick} aria-label="menu">
          <MenuIcon />
        </IconButton>
        <Box display="flex" alignItems="center" gap={1} sx={{ flexGrow: 1 }}>
          <img src="/assets/logo.svg" alt="logo" height={28} />
          <Typography
            variant="h6"
            className="gradient-text"
            sx={{ display: { xs: 'none', sm: 'block' }, fontWeight: 700 }}
          >
            {APP_NAME}
          </Typography>
        </Box>

        <Tooltip title={mode === 'dark' ? 'Светлая тема' : 'Тёмная тема'}>
          <IconButton onClick={toggleTheme}>
            {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Tooltip>

        <Tooltip title={user?.email || 'Профиль'}>
          <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
            <Avatar sx={{ width: 32, height: 32, background: 'linear-gradient(135deg,#2563EB,#7C3AED)' }}>
              {initials}
            </Avatar>
          </IconButton>
        </Tooltip>
        <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
          <MenuItem
            onClick={() => {
              setAnchorEl(null)
              logout()
              navigate('/login')
            }}
          >
            <LogoutIcon fontSize="small" sx={{ mr: 1 }} /> Выйти
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  )
}

export default Header
