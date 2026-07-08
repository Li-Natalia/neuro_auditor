import { GlobalStyles as MuiGlobalStyles } from '@mui/material'
import { palette, gradients } from './tokens'

export const GlobalStyles = () => (
  <MuiGlobalStyles
    styles={{
      'html, body, #root': {
        margin: 0,
        padding: 0,
        height: '100%',
        width: '100%',
      },
      body: {
        fontFamily: '"Inter", "Roboto", system-ui, sans-serif',
        backgroundColor: palette.bgLight,
        transition: 'background-color 0.3s ease',
      },
      a: { textDecoration: 'none', color: 'inherit' },
      '.gradient-text': {
        background: gradients.primary,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      },
      '.gradient-bg': { background: gradients.primary },
      '@keyframes fadeIn': {
        '0%': { opacity: 0, transform: 'translateY(8px)' },
        '100%': { opacity: 1, transform: 'translateY(0)' },
      },
      '.fade-in': { animation: 'fadeIn 0.3s ease' },
    }}
  />
)
