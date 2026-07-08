// Shared design tokens (see README palette)
import { createTheme } from '@mui/material/styles'

export const palette = {
  primary: '#2563EB',
  primaryDark: '#1D4ED8',
  secondary: '#7C3AED',
  secondaryDark: '#6D28D9',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#0EA5E9',
  bgLight: '#F8FAFC',
  bgDark: '#0F172A',
  textLight: '#1E293B',
  textDark: '#F1F5F9',
} as const

export const gradients = {
  primary: `linear-gradient(135deg, ${palette.primary} 0%, ${palette.secondary} 100%)`,
  primarySoft: `linear-gradient(135deg, rgba(37,99,235,0.12) 0%, rgba(124,58,237,0.12) 100%)`,
  successSoft: `linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(5,150,105,0.12) 100%)`,
  dangerSoft: `linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(220,38,38,0.12) 100%)`,
} as const

export const sharedTypography = {
  fontFamily: '"Inter", "Roboto", system-ui, sans-serif',
  h1: { fontFamily: '"Poppins", "Inter", sans-serif', fontWeight: 700 },
  h2: { fontFamily: '"Poppins", "Inter", sans-serif', fontWeight: 700 },
  h3: { fontFamily: '"Poppins", "Inter", sans-serif', fontWeight: 600 },
  h4: { fontFamily: '"Poppins", "Inter", sans-serif', fontWeight: 600 },
  h5: { fontFamily: '"Poppins", "Inter", sans-serif', fontWeight: 600 },
  h6: { fontFamily: '"Poppins", "Inter", sans-serif', fontWeight: 600 },
  button: { textTransform: 'none', fontWeight: 600 },
} as const

export const sharedShadows = [
  'none',
  '0 1px 2px rgba(15,23,42,0.06)',
  '0 2px 8px rgba(15,23,42,0.08)',
  '0 4px 12px rgba(15,23,42,0.10)',
  '0 8px 24px rgba(15,23,42,0.12)',
  ...Array(19).fill('0 12px 28px rgba(15,23,42,0.14)'),
] as const

export function createBaseTheme(mode: 'light' | 'dark') {
  const isDark = mode === 'dark'
  return createTheme({
    palette: {
      mode,
      primary: { main: palette.primary, dark: palette.primaryDark },
      secondary: { main: palette.secondary, dark: palette.secondaryDark },
      success: { main: palette.success },
      warning: { main: palette.warning },
      error: { main: palette.error },
      info: { main: palette.info },
      background: {
        default: isDark ? palette.bgDark : palette.bgLight,
        paper: isDark ? '#1E293B' : '#FFFFFF',
      },
      text: {
        primary: isDark ? palette.textDark : palette.textLight,
        secondary: isDark ? '#94A3B8' : '#64748B',
      },
    },
    typography: sharedTypography as any,
    shape: { borderRadius: 12 },
    shadows: sharedShadows as any,
    components: {
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: { borderRadius: 10, transition: 'all 0.2s ease' },
          containedPrimary: {
            background: gradients.primary,
            color: '#FFFFFF',
            '&:hover': { background: gradients.primary, color: '#FFFFFF', opacity: 0.92, transform: 'translateY(-1px)' },
          },
        },
      },
      MuiCard: { styleOverrides: { root: { borderRadius: 16, backgroundImage: 'none' } } },
      MuiPaper: { styleOverrides: { root: { backgroundImage: 'none' } } },
      MuiAppBar: { defaultProps: { elevation: 0, color: 'transparent' } },
      MuiTextField: { defaultProps: { variant: 'outlined' } },
    },
  })
}
