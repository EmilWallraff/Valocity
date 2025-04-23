/** @type {import('tailwindcss').Config} */
import defaultTheme from 'tailwindcss/defaultTheme'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
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
            DEFAULT: '#0A0A0A',
            dark: '#0A0A0A',
            light: '#0A0A0A', 
          },
      },
    },
  },
  plugins: [
    require('tailwind-scrollbar'),
  ],
  
}
