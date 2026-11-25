import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// SITE_BASE permite desplegar en una subruta (p. ej. GitHub Pages: /SaludVital/)
export default defineConfig({
  integrations: [react()],
  base: process.env.SITE_BASE ?? '/',
  devToolbar: { enabled: false },
});
