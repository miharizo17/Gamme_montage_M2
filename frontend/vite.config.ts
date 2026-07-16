import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/front-gamme_montage/',
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api/coupe/planification': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/api': {
        target: 'https://erp.loimada.com:1467/api',
        //  target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
