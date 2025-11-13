import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Keep the '/api' prefix so Flask routes like '/api/wake-word' work as-is
        // Removing it would proxy to '/wake-word', which our backend does not handle for POST
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
