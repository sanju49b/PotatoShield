/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        orange: {
          DEFAULT: '#FF6B35',
          dark: '#FF4500',
          light: '#FF8C42',
        },
        green: {
          DEFAULT: '#4CAF50',
          dark: '#388E3C',
          light: '#66BB6A',
        },
        black: {
          DEFAULT: '#000000',
          light: '#0A0A0A',
        },
      },
      fontFamily: {
        robotic: ['Orbitron', 'monospace'],
      },
    },
  },
  plugins: [],
}

