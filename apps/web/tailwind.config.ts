import type { Config } from 'tailwindcss';

/**
 * Tokens del UI Design System (03-UI_DESIGN_SYSTEM.md).
 * Todo estilo debe resolverse con estos tokens.
 */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0F0F10',
        surface: '#1C1C1E',
        surfaceElevated: '#242426',
        border: '#2C2C2E',
        textPrimary: '#F5F5F7',
        textSecondary: '#A1A1A6',
        textMuted: '#6E6E73',
        primary: '#0071E3',
        success: '#30D158',
        warning: '#FFD60A',
        danger: '#FF453A',
        info: '#64D2FF',
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        display: ['48px', { fontWeight: '600' }],
        title: ['32px', { fontWeight: '600' }],
        subtitle: ['24px', { fontWeight: '600' }],
        heading: ['20px', { fontWeight: '600' }],
        body: ['16px', { fontWeight: '400' }],
        description: ['14px', { fontWeight: '400' }],
        label: ['13px', { fontWeight: '500' }],
      },
      borderRadius: {
        control: '14px',
        card: '20px',
      },
      boxShadow: {
        soft: '0 4px 20px rgba(0, 0, 0, 0.18)',
      },
      maxWidth: {
        layout: '1600px',
      },
    },
  },
  plugins: [],
} satisfies Config;
