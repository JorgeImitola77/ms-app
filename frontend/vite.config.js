import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Proxy hacia n8n para evitar CORS desde el navegador.
    // El frontend llama /n8n/* y Vite (dentro del contenedor) lo reenvía a n8n:5678.
    proxy: {
      '/n8n': {
        target: process.env.N8N_PROXY_TARGET || 'http://n8n:5678',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/n8n/, ''),
      },
    },
  },
  // Expone las variables VITE_* del entorno de Node (pasadas por docker-compose)
  // como import.meta.env.VITE_* dentro del código React
  define: {
    'import.meta.env.VITE_AUTH0_DOMAIN':    JSON.stringify(process.env.VITE_AUTH0_DOMAIN    ?? ''),
    'import.meta.env.VITE_AUTH0_CLIENT_ID': JSON.stringify(process.env.VITE_AUTH0_CLIENT_ID ?? ''),
    'import.meta.env.VITE_AUTH0_AUDIENCE':  JSON.stringify(process.env.VITE_AUTH0_AUDIENCE  ?? ''),
    'import.meta.env.VITE_N8N_RAG_URL':     JSON.stringify(process.env.VITE_N8N_RAG_URL     ?? '/n8n/webhook/rag-consulta'),
  },
})
