import { Snackbar, Alert, Slide } from '@mui/material'
import { useThemeStore } from '../../../store/slices/uiSlice'

export function NotificationHost() {
  const { notifications, dismissNotification } = useThemeStore()
  return (
    <>
      {notifications.map((n) => (
        <Snackbar
          key={n.id}
          open
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          TransitionComponent={(props) => <Slide {...props} direction="up" />}
          autoHideDuration={5000}
          onClose={() => dismissNotification(n.id)}
        >
          <Alert
            severity={n.severity}
            variant="filled"
            onClose={() => dismissNotification(n.id)}
            sx={{ borderRadius: 2, minWidth: 280 }}
          >
            {n.message}
          </Alert>
        </Snackbar>
      ))}
    </>
  )
}

export default NotificationHost
