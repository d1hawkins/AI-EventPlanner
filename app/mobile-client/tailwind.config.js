/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4E73DF',
          dark: '#2e59d9',
          light: '#6f8fef',
        },
        success: {
          DEFAULT: '#1CC88A',
          dark: '#17a673',
          light: '#43d9a1',
        },
        warning: {
          DEFAULT: '#F6C23E',
          dark: '#dda20a',
          light: '#f8ce65',
        },
        danger: {
          DEFAULT: '#E74A3B',
          dark: '#d32f2f',
          light: '#eb6b5f',
        },
        dark: {
          DEFAULT: '#2E3440',
          light: '#4c566a',
        },
        gray: {
          DEFAULT: '#858796',
          light: '#E3E6F0',
          bg: '#F8F9FC',
        },
        // Dark mode specific colors
        'dark-bg': {
          primary: '#1a1b1e',
          secondary: '#25262b',
          tertiary: '#2c2d32',
        },
        'dark-text': {
          primary: '#e4e5e9',
          secondary: '#a6a7ab',
          tertiary: '#696a70',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'pill': '999px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0,0,0,0.05)',
        'md': '0 4px 6px rgba(0,0,0,0.1)',
        'lg': '0 10px 15px rgba(0,0,0,0.1)',
        'xl': '0 20px 25px rgba(0,0,0,0.1)',
      },
    },
  },
  plugins: [],
}
