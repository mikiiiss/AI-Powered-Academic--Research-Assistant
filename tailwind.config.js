export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        'glass-gradient': 'linear-gradient(113deg, rgba(255, 255, 255, 0.20) 0%, rgba(255, 255, 255, 0.20) 110.84%)',
        'glass-gradient-strong': 'linear-gradient(113deg, rgba(255, 255, 255, 0.20) 0%, rgba(255, 255, 255, 0.40) 110.84%)',
        'main-gradient': 'linear-gradient(239deg, rgb(140, 145, 165) -59.4%, rgb(5, 127, 209) 633.58%)',
      },
      backdropBlur: {
        '21': '21px',
      },
      borderRadius: {
        '20': '20px',
      },
    },
  },
  plugins: [],
}
