/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'swa-blue': '#304CB2',
        'swa-gold': '#FFBF00',
        'swa-red': '#C8102E',
        'neutral-900': '#0f172a',
        'neutral-800': '#1e293b',
        'neutral-700': '#334155',
        'neutral-600': '#475569',
      },
      backgroundColor: {
        'dark-bg': '#0f172a',
        'dark-surface': '#1e293b',
      },
      textColor: {
        'dark-primary': '#f1f5f9',
        'dark-secondary': '#cbd5e1',
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
