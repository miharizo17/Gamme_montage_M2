import { defineConfig, devices } from '@playwright/test'

// Suite E2E persistee (frontend <-> backend <-> moteur IA), a executer
// contre un backend FastAPI deja demarre (par defaut sur le port 8000 ;
// surchargeable via E2E_BACKEND_PORT pour cibler une instance isolee).
// Voir e2e/README.md pour le mode d'emploi complet.
const PORT = 3055

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  reporter: [['list']],
  use: {
    baseURL: `http://localhost:${PORT}/front-gamme_montage/`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  webServer: {
    command: 'npx vite --config vite.config.e2e.ts',
    url: `http://localhost:${PORT}/front-gamme_montage/`,
    reuseExistingServer: true,
    timeout: 30_000,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})
