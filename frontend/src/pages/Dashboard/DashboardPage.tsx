import { Typography } from '@mui/material'
import { Dashboard } from '../../components/dashboard/Dashboard'

export function DashboardPage() {
  return (
    <>
      <Typography variant="h4" mb={2} className="gradient-text">
        Дашборд
      </Typography>
      <Dashboard />
    </>
  )
}

export default DashboardPage
