/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./webapp/templates/webapp/**/*.{html,js}",
    "./static/css/styles/*.css",
  ],
  theme: {
    daisyui: {
      themes: [
        {
          mytheme: {
            
  "primary": "#a855f7",
            
  "secondary": "#f43f5e",
            
  "accent": "#22d3ee",
            
  "neutral": "#ff00ff",
            
  "base-100": "#f5f5f4",
            
  "info": "#facc15",
            
  "success": "#4ade80",
            
  "warning": "#f97316",
            
  "error": "#ef4444",
            },
          },
        ],
      },
  },
  plugins: [
    require('daisyui'),
  ],
}

