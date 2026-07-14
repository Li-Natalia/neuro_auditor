import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  Tabs,
  Tab,
  InputAdornment,
  IconButton,
  Divider,
  Link,
} from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { loginSchema, registerSchema, type LoginFormData, type RegisterFormData } from '../../utils/validators'
import { palette } from '../../themes/tokens'
import { APP_NAME } from '../../utils/constants'
import { getErrorMessage } from '../../utils/helpers'

export function LoginPage() {
  const navigate = useNavigate()
  const { login, register: registerUser } = useAuth()
  const [tab, setTab] = useState(0)
  const [showPassword, setShowPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register: rhfRegister,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<LoginFormData & RegisterFormData>({
    resolver: zodResolver(tab === 0 ? (loginSchema as any) : (registerSchema as any)),
    defaultValues: { email: '', password: '', name: '', confirmPassword: '' },
  })

  const onSubmit = async (data: LoginFormData & RegisterFormData) => {
    setServerError(null)
    try {
      if (tab === 0) {
        await login({ email: data.email, password: data.password })
      } else {
        await registerUser({
          name: data.name,
          email: data.email,
          password: data.password,
          confirmPassword: data.confirmPassword,
        })
      }
      navigate('/')
    } catch (e) {
      setServerError(getErrorMessage(e))
    }
  }

  const switchTab = (_: unknown, v: number) => {
    setTab(v)
    setServerError(null)
    reset()
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: `linear-gradient(135deg, ${palette.primary} 0%, ${palette.secondary} 100%)`,
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: '100%' }} elevation={8}>
        <CardContent sx={{ p: 4 }}>
          <Box textAlign="center" mb={2}>
            <img src="/assets/logo.svg" alt="logo" height={48} />
            <Typography variant="h5" mt={2} fontWeight={700}>
              {APP_NAME}
            </Typography>
            <Typography color="text.secondary">Анализ финансовой отчетности</Typography>
          </Box>

          <Tabs value={tab} onChange={switchTab} variant="fullWidth" sx={{ mb: 2 }}>
            <Tab label="Вход" />
            <Tab label="Регистрация" />
          </Tabs>

          {serverError && <Alert severity="error" sx={{ mb: 2 }}>{serverError}</Alert>}

          <form onSubmit={handleSubmit(onSubmit)}>
            {tab === 1 && (
              <TextField
                label="Имя"
                fullWidth
                margin="normal"
                error={!!errors.name}
                helperText={errors.name?.message}
                {...rhfRegister('name')}
              />
            )}
            <TextField
              label="Email"
              type="email"
              fullWidth
              margin="normal"
              error={!!errors.email}
              helperText={errors.email?.message}
              {...rhfRegister('email')}
            />
            <TextField
              label="Пароль"
              type={showPassword ? 'text' : 'password'}
              fullWidth
              margin="normal"
              error={!!errors.password}
              helperText={errors.password?.message}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword((s) => !s)} edge="end">
                      {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              {...rhfRegister('password')}
            />
            {tab === 1 && (
              <TextField
                label="Подтвердите пароль"
                type="password"
                fullWidth
                margin="normal"
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword?.message}
                {...rhfRegister('confirmPassword')}
              />
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isSubmitting}
              sx={{ mt: 2 }}
            >
              {tab === 0 ? 'Войти' : 'Зарегистрироваться'}
            </Button>
          </form>

          {tab === 0 && (
            <>
              <Divider sx={{ my: 2 }}>или</Divider>
              <Link
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  setServerError('Восстановление пароля будет доступно позже')
                }}
                display="block"
                textAlign="center"
                variant="body2"
              >
                Забыли пароль?
              </Link>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default LoginPage
