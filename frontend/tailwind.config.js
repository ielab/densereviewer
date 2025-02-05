/** @type {import('tailwindcss').Config} */
import { colors as defaultColors } from 'tailwindcss/defaultTheme'
import { screens as defaultScreens } from 'tailwindcss/defaultTheme'

export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      screens: {
        ...defaultScreens,
        ...{
          'theme-lg': '992px',
        },
      },
      colors: {
        ...defaultColors,
        ...{
          primary: {
            50: '#faf5ff',
            100: '#f3e8ff',
            200: '#e9d5ff',
            500: '#a855f7',
            800: '#6b21a8',
          },
        },
      },
    },
  },
  important: true,
  plugins: [],
  prefix: 'tw-',
  corePlugins: {
    preflight: false,
  },
}
