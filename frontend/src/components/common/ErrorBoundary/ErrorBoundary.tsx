import { Component, ErrorInfo, ReactNode } from 'react'
import { Box, Button, Typography } from '@mui/material'

interface Props {
  children: ReactNode
}
interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          height="100vh"
          gap={2}
          p={4}
          textAlign="center"
        >
          <Typography variant="h4" color="error">
            Что-то пошло не так
          </Typography>
          <Typography color="text.secondary" maxWidth={480}>
            {this.state.error?.message || 'Непредвиденная ошибка приложения.'}
          </Typography>
          <Button variant="contained" onClick={this.handleReset}>
            Попробовать снова
          </Button>
        </Box>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
