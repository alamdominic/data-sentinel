# DATA SENTINEL — Frontend (Web)

React + TypeScript + Vite + TailwindCSS. Consume la API REST del backend; sin lógica de negocio (todo cálculo/validación vive en el backend).

Design system detallado: [../../steps/03-UI_DESIGN_SYSTEM.md](../../steps/03-UI_DESIGN_SYSTEM.md).

---

## Estructura

```text
src/
├── app/          Bootstrap de React, router, providers globales (QueryClient, Auth)
├── pages/        Pantallas: Login, Dashboard, Ejecuciones, Detalle, Historial, Estadísticas, Administración
├── features/     Módulos por dominio (auth, dashboard, executions, statistics, etl-registry)
├── components/   Componentes reutilizables (Button, Card, DataTable, FilterPanel, layout/...)
├── services/     Clientes HTTP hacia la API. Sin reglas de negocio
└── styles/       Tokens Tailwind del design system
```

---

## Desarrollo local

Se instala desde la **raíz del monorepo** (usa npm workspaces, comparte `packages/types` y `packages/utils`):

```powershell
cd C:\Users\PracticanteBI\Documents\DataSentinel
npm install
copy apps\web\.env.example apps\web\.env
npm run dev:web
```

Abre <http://localhost:5173>. Requiere el backend corriendo (ver [../api/README.md](../api/README.md)).

---

## Variables de entorno

| Variable | Descripción |
|---|---|
| `VITE_API_BASE_URL` | URL base del backend, ej. `http://localhost:8000` en desarrollo, `https://tu-dominio.com` en producción |

> **Importante — gotcha de Vite:** las variables `VITE_*` se **incrustan en el JavaScript durante el `build`**, no se leen en tiempo de ejecución. Si cambias `VITE_API_BASE_URL` después de compilar, el cambio **no** se aplica hasta que vuelvas a correr `npm run build:web`. No existe forma de "editar el .env en el servidor" y que el frontend ya construido lo recoja — hay que reconstruir.

---

## Tests y build

```powershell
npm run test:web     # vitest (28 tests)
npm run build:web    # tsc --noEmit + vite build -> apps/web/dist/
npm run lint:web      # solo type-check
```

`npm run build:web` es lo que genera los archivos estáticos que se sirven en producción (`apps/web/dist/index.html`, `assets/*.js`, `assets/*.css`).

---

## Despliegue en producción

Se empaqueta con Docker. La imagen sirve el build estático con nginx y resuelve el gotcha de `VITE_*` con un mecanismo de runtime: `docker/docker-entrypoint.sh` genera `env.js` (via `envsubst`) con la variable `API_BASE_URL` real **al arrancar el contenedor**, y [apiClient.ts](src/services/apiClient.ts) la lee desde `window.__ENV__` antes que la de build time. Así cambiar la URL del API no exige reconstruir la imagen.

- [../../docs/DEPLOY_DOCKER.md](../../docs/DEPLOY_DOCKER.md): cómo está armado el empaquetado, build y prueba local.
- [../../docs/DEPLOY_VPS.md](../../docs/DEPLOY_VPS.md): runbook real de producción (build + push a Docker Hub, pull en el VPS).

### Checklist antes de desplegar

- [ ] `API_BASE_URL` en el `.env` de producción está vacío (mismo origen) o apunta a la URL correcta si el API vive en otro dominio
- [ ] `npm run build:web` (o `docker compose build`) corre sin errores de tipos
- [ ] `docker compose push` subió ambas imágenes a Docker Hub antes de hacer `pull` en el VPS
- [ ] `CORS_ALLOWED_ORIGINS` del backend incluye el dominio donde se sirve este frontend
