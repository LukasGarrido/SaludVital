# syntax=docker/dockerfile:1
# Dashboard de Astro. Targets:
#   dev   -> servidor de desarrollo con recarga en caliente (puerto 4321)
#   prod  -> sitio estático servido por nginx sin privilegios (puerto 8080)  [por defecto]

# ── Dependencias (capa cacheada mientras no cambie package*.json) ──
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ── Desarrollo ──
FROM deps AS dev
ENV HOST=0.0.0.0
COPY . .
EXPOSE 4321
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4321"]

# ── Build estático ──
FROM deps AS build
# Subruta de despliegue (p. ej. /SaludVital/ en GitHub Pages)
ARG SITE_BASE=/
ENV SITE_BASE=${SITE_BASE}
COPY . .
RUN npm run build

# ── Producción ──
FROM nginxinc/nginx-unprivileged:1.27-alpine AS prod
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/healthz >/dev/null || exit 1
