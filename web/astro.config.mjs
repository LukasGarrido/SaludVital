import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// SITE_BASE permite desplegar en una subruta (p. ej. GitHub Pages: /SaludVital/)
export default defineConfig({
  integrations: [react()],
  base: process.env.SITE_BASE ?? '/',
  devToolbar: { enabled: false },
  vite: {
    // En Docker (bind mounts) los eventos de archivo no llegan: se activa polling con CHOKIDAR_USEPOLLING=true
    server: { watch: { usePolling: process.env.CHOKIDAR_USEPOLLING === 'true' } },
  },
});
