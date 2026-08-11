import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Config Vite dediee aux tests E2E (playwright.config.ts) : port et
// backend cible isoles de la session de dev habituelle (ports 3001/8000),
// pour ne jamais la perturber. Volontairement a la racine (pas dans e2e/)
// pour que la resolution de `root`/node_modules reste identique a
// vite.config.ts.
const backendPort = process.env.E2E_BACKEND_PORT ?? '8000'

export default defineConfig({
  base: '/front-gamme_montage/',
  plugins: [react()],
  server: {
    port: 3055,
    strictPort: true,
    proxy: {
      '/api/gamme-montage': {
        target: `http://127.0.0.1:${backendPort}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/gamme-montage/, ''),
      },
    },
  },
})
