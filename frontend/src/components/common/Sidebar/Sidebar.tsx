import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
} from '@mui/material'
import { useLocation, useNavigate } from 'react-router-dom'
import DashboardIcon from '@mui/icons-material/Dashboard'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import AnalyticsIcon from '@mui/icons-material/Analytics'
import DescriptionIcon from '@mui/icons-material/Description'
import ChatIcon from '@mui/icons-material/Chat'
import { ROUTES } from '../../../utils/constants'

const NAV_ITEMS = [
  { path: ROUTES.DASHBOARD, label: 'Дашборд', icon: DashboardIcon },
  { path: ROUTES.UPLOAD, label: 'Загрузка', icon: UploadFileIcon },
  { path: ROUTES.ANALYSIS, label: 'Анализ', icon: AnalyticsIcon },
  { path: ROUTES.REPORTS, label: 'Отчёты', icon: DescriptionIcon },
  { path: ROUTES.CHAT, label: 'Чат-бот', icon: ChatIcon },
] as const

export const DRAWER_WIDTH = 260

function NavContent({ onNavigate }: { onNavigate?: () => void }) {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <Box sx={{ overflow: 'auto', px: 1, py: 3 }}>
      <List>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path
          const Icon = item.icon
          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                selected={isActive}
                onClick={() => {
                  navigate(item.path)
                  onNavigate?.()
                }}
                sx={{
                  borderRadius: 2,
                  mb: 0.5,
                  '&.Mui-selected': {
                    background: 'linear-gradient(135deg, rgba(37,99,235,0.12), rgba(124,58,237,0.12))',
                    '&:hover': {
                      background: 'linear-gradient(135deg, rgba(37,99,235,0.18), rgba(124,58,237,0.18))',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: isActive ? 'primary.main' : 'inherit' }}>
                  <Icon />
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{ fontWeight: isActive ? 600 : 400 }}
                />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
      <Divider sx={{ my: 2 }} />
      <Box px={2}>
        <Typography variant="caption" color="text.secondary">
          Версия 0.1.0
        </Typography>
      </Box>
    </Box>
  )
}

interface Props {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: Props) {
  return (
    <Box
      component="nav"
      sx={{
        width: { md: DRAWER_WIDTH },
        flexShrink: { md: 0 },
      }}
    >
      {/* Permanent (in-flow) sidebar: desktop */}
      <Box
        sx={{
          display: { xs: 'none', md: 'block' },
          width: DRAWER_WIDTH,
          height: '100%',
          position: 'sticky',
          top: 64,
          borderRight: (t) => `1px solid ${t.palette.divider}`,
          backgroundColor: (t) => (t.palette.mode === 'dark' ? 'rgba(30,41,59,0.4)' : 'rgba(248,250,252,0.6)'),
          backdropFilter: 'blur(8px)',
        }}
      >
        <NavContent />
      </Box>

      {/* Temporary drawer: mobile */}
      <Drawer
        variant="temporary"
        anchor="left"
        open={open}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            borderRight: (t) => `1px solid ${t.palette.divider}`,
          },
        }}
      >
        <NavContent onNavigate={onClose} />
      </Drawer>
    </Box>
  )
}

export default Sidebar
