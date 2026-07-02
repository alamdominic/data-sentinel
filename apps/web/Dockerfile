# DATA SENTINEL Web — build multi-stage.
# Contexto de build: la RAIZ del monorepo (necesita packages/types y
# packages/utils via npm workspaces). Ver docker-compose.yml: context: .
#
# Nota: VITE_API_BASE_URL de aqui NO se usa en produccion — la URL real del
# API se inyecta en runtime via env.js (ver docker/docker-entrypoint.sh).
# Este build-time value solo aplicaria si alguien corriera esta imagen sin
# el entrypoint, lo cual no es el caso.

FROM node:20-alpine AS build
WORKDIR /repo

COPY package.json package-lock.json ./
COPY packages/types/package.json packages/types/package.json
COPY packages/utils/package.json packages/utils/package.json
COPY apps/web/package.json apps/web/package.json
RUN npm ci

COPY packages ./packages
COPY apps/web ./apps/web
RUN npm run build --workspace @datasentinel/web

FROM nginx:1.27-alpine AS runtime

RUN rm -f /etc/nginx/conf.d/default.conf
COPY apps/web/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY apps/web/docker/env.template.js /usr/share/nginx/html/env.template.js
COPY apps/web/docker/docker-entrypoint.sh /docker-entrypoint.d/99-datasentinel-env.sh
RUN chmod +x /docker-entrypoint.d/99-datasentinel-env.sh

COPY --from=build /repo/apps/web/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
