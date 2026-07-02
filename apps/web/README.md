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

Con Docker (recomendado): [../../docs/DEPLOY_DOCKER.md](../../docs/DEPLOY_DOCKER.md). La imagen sirve el build estático con nginx y resuelve el gotcha de `VITE_*` con un mecanismo de runtime: `docker/docker-entrypoint.sh` genera `public/env.js` (via `envsubst`) con la variable `API_BASE_URL` real **al arrancar el contenedor**, y [apiClient.ts](src/services/apiClient.ts) la lee desde `window.__ENV__` antes que la de build time. Así cambiar la URL del API no exige reconstruir la imagen.

Sin contenedores, VPS con nginx + systemd: [../../docs/DEPLOY_VPS.md](../../docs/DEPLOY_VPS.md). Resumen de esta capa:

1. En el servidor (o en tu máquina, si vas a subir el resultado): configura `apps/web/.env` con `VITE_API_BASE_URL` apuntando al **dominio público real** (ej. `https://datasentinel.tuempresa.com`).
2. Compila:
   ```bash
   npm install
   npm run build:web
   ```
3. El resultado es una carpeta **estática** (`apps/web/dist/`) — no necesita Node.js corriendo en producción, ni proceso, ni puerto propio. Solo se sirve como archivos planos.
4. nginx sirve `dist/` como root del sitio, con `try_files $uri /index.html` (necesario porque la app usa client-side routing con `react-router-dom`; sin esto, refrescar una ruta como `/executions/123` da 404).
5. Cada vez que haya un cambio de código: `npm run build:web` de nuevo y reemplazar el contenido de `dist/` en el servidor. No hay "reinicio de servicio" para el frontend — son archivos estáticos.

### Checklist antes de desplegar

- [ ] `VITE_API_BASE_URL` apunta al dominio de producción (no a `localhost`)
- [ ] `npm run build:web` corre sin errores de tipos
- [ ] El backend en ese mismo dominio ya responde en `/api/health`
- [ ] `CORS_ALLOWED_ORIGINS` del backend incluye el dominio donde se sirve este frontend
