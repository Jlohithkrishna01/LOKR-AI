/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0d0d0d',
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        secondary: {
          DEFAULT: '#525252',
          50: '#fafafa',
          100: '#f5f5f5',
          500: '#737373',
          600: '#525252',
          700: '#404040',
        },
        accent: {
          DEFAULT: '#10a37f',
          500: '#10a37f',
          600: '#0d8a6c',
        },
        dark: {
          bg: '#0d0d0d',
          surface: '#171717',
          card: '#212121',
          cardHover: '#2a2a2a',
          border: '#2f2f2f',
          muted: '#8e8e8e',
          text: '#ececec',
        },
        light: {
          bg: '#ffffff',
          surface: '#f9f9f9',
          card: '#f4f4f4',
          cardHover: '#ececec',
          border: '#e5e5e5',
          muted: '#6b7280',
          text: '#0d0d0d',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
      },
      boxShadow: {
        'subtle': '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)',
        'premium': '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05)',
        'glow': '0 0 20px rgba(0, 0, 0, 0.25)',
      }
    },
  },
  plugins: [],
}
