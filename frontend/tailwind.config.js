/** @type {import('tailwindcss').Config} */
import defaultTheme from 'tailwindcss/defaultTheme'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    'text-brand',
    'text-accent',
    'text-element-lighter',
    'bg-element',
    'bg-element-light',
    'bg-element-dark',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
        raj: ['Rajdhani', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        brand: {
          DEFAULT: '#00FFFF',
          dark: '#00CCCC',
          light: '#66FFFF',
        },
        accent: {
          DEFAULT: '#FF4655',
          dark: '#CC3844',
          light: '#FF6B77', 
        },
        darkness: {
          DEFAULT: '#161616',
          dark: '#161616',
          light: '#161616', 
        },
        element: {
          DEFAULT: '#1F2937',
          dark: '#111827',
          light: '#374151',
          lighter: '#4B5563',
      },
      },
    },
  },
  plugins: [
    require('tailwind-scrollbar'),
  ],
  
}
