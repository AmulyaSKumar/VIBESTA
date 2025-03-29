/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        festival: {
          primary: '#FF6B6B',    // Vibrant warm red
          secondary: '#FFD166',  // Festive yellow/gold
          accent: '#06D6A0',     // Bright turquoise
          dark: '#073B4C',       // Deep blue for contrast
          light: '#FFF7ED',      // Warm off-white
          orange: '#F76E11',     // Vibrant orange
          purple: '#9B5DE5',     // Festive purple
          pink: '#F15BB5',       // Bright pink
        }
      },
      fontFamily: {
        'display': ['Poppins', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'festival-pattern': "url('/static/img/festival-pattern.png')",
        'diya-pattern': "url('/static/img/diya-pattern.png')",
        'confetti': "url('/static/img/confetti.png')",
      },
      boxShadow: {
        'festival': '0 4px 14px 0 rgba(255, 107, 107, 0.39)',
      },
      animation: {
        'festival-pulse': 'festival-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        'festival-pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.7 },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '2rem',
      }
    },
  },
  plugins: [],
} 