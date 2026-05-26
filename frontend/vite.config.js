import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
  // Expone las variables VITE_* del entorno de Node (pasadas por docker-compose)
  // como import.meta.env.VITE_* dentro del código React
  define: {
    'import.meta.env.VITE_AUTH0_DOMAIN':    JSON.stringify(process.env.VITE_AUTH0_DOMAIN    ?? ''),
    'import.meta.env.VITE_AUTH0_CLIENT_ID': JSON.stringify(process.env.VITE_AUTH0_CLIENT_ID ?? ''),
    'import.meta.env.VITE_AUTH0_AUDIENCE':  JSON.stringify(process.env.VITE_AUTH0_AUDIENCE  ?? ''),
  },
})
