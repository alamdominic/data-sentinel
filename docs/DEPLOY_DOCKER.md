# DATA SENTINEL — Despliegue con Docker

Dos contenedores (`api` + `web`) orquestados con `docker compose`. Alternativa a [DEPLOY_VPS.md](DEPLOY_VPS.md) (nginx + systemd sin contenedores) — usa esta guía si vas a desplegar con Docker.

---

## Arquitectura

```text
Internet
   │
   ▼
contenedor "web" (nginx, puerto host 8080 -> 80)
   ├── sirve el frontend compilado (estatico)
   └── proxya /api/ -> http://api:8000/api/  (red interna de compose)
                              │
                              ▼
                        contenedor "api" (uvicorn, sin puerto publicado)
                              │
                              ▼
                        PostgreSQL (RDS u otro host, fuera de Docker)
```

El backend **no publica ningún puerto al host** — solo es alcanzable desde `web` a través de la red interna de compose (`http://api:8000`). Si necesitas TLS público, ponlo delante de `web` (nginx/Caddy/Traefik del host, o certbot apuntando al puerto 8080) — esta guía no lo cubre, ver [DEPLOY_VPS.md](DEPLOY_VPS.md) para el patrón de certbot.

---

## Inyección de variables: en la creación del contenedor, no en el build

Ambos servicios reciben su configuración como variables de entorno **al crear/arrancar el contenedor** (`docker compose up`), no horneadas en la imagen:

- **`api`**: lee `DB_HOST`, `AUTH_SECRET_KEY`, etc. al arrancar el proceso uvicorn — normal en cualquier app 12-factor.
- **`web`**: Vite normalmente hornea sus variables en el build, pero aquí se evitó con un mecanismo de runtime: al arrancar el contenedor, `docker/docker-entrypoint.sh` genera `env.js` (via `envsubst` sobre `docker/env.template.js`) con el valor real de `API_BASE_URL`, y `index.html` lo carga antes del bundle (`window.__ENV__.API_BASE_URL`). El frontend en [apiClient.ts](../apps/web/src/services/apiClient.ts) prioriza ese valor sobre el de build time.

Consecuencia práctica: cambiar cualquier variable (`DB_PASSWORD`, `API_BASE_URL`, lo que sea) solo requiere `docker compose up -d` de nuevo — **nunca** hace falta reconstruir las imágenes por un cambio de configuración.

---

## Paso 1 — Configurar variables

```bash
cp .env.docker.example .env
```

Edita `.env` (junto a `docker-compose.yml`, en la raíz del repo) con tus datos reales. Variables clave:

| Variable | Notas |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión a PostgreSQL |
| `AUTH_SECRET_KEY` | Generar una nueva para producción: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `CORS_ALLOWED_ORIGINS` | Dominio público donde se sirve el frontend (ej. `https://datasentinel.tuempresa.com` o `http://localhost:8080` en local) |
| `API_BASE_URL` | Vacío (recomendado) = mismo origen, el nginx de `web` proxya `/api` internamente. Solo pon una URL absoluta si el backend va a vivir en otro dominio/puerto público |
| `WEB_PORT` | Puerto del host mapeado al contenedor `web` (default `8080`) |

`.env` está gitignorado — nunca se versiona con credenciales reales.

---

## Paso 2 — Build y arranque

```bash
docker compose build
docker compose up -d
```

Verificar:

```bash
curl http://localhost:8080/api/health
# {"status":"ok","database":"up"}
```

Abre `http://localhost:8080` en el navegador.

---

## Paso 3 — Crear el primer usuario

Los scripts de administración (`create_user.py`, `change_password.py`) **no corren dentro de los contenedores** — son scripts locales que se conectan directo a la base de datos (necesitan `DATABASE_ADMIN_URL` en `scripts/.env`, ver [CREAR_USUARIOS.md](CREAR_USUARIOS.md)). Puedes correrlos desde tu máquina, desde el VPS host, o dentro del propio contenedor `api` si prefieres no instalar Python fuera de Docker:

```bash
docker compose exec api python /app/../../scripts/create_user.py becario.bi@lazarza.com.mx "Tu Nombre" admin
```

> Nota: `scripts/` no se copia dentro de la imagen `api` (ver `.dockerignore`). Si quieres correrlo *dentro* del contenedor, monta el volumen `./scripts:/scripts` en `docker-compose.yml` primero, o simplemente ejecútalo desde el host apuntando `DATABASE_ADMIN_URL` a la misma base — es lo más simple y no requiere tocar el compose.

---

## Actualizar tras cambios de código

```bash
docker compose build
docker compose up -d
```

Docker solo reconstruye las capas que cambiaron (cache por capas) — si solo tocaste el frontend, el rebuild del backend es prácticamente instantáneo (cache hit).

## Ver logs

```bash
docker compose logs -f api
docker compose logs -f web
```

## Apagar

```bash
docker compose down
```

---

## Troubleshooting

| Síntoma | Causa | Solución |
|---|---|---|
| `web` arriba pero `/api/health` da 502 | `api` no arrancó o tronó al conectar a la base | `docker compose logs api` |
| Login falla con error de red desde el navegador | `API_BASE_URL` mal, o `CORS_ALLOWED_ORIGINS` no incluye el origen real | Revisa `.env`, `docker compose up -d` de nuevo (no hace falta rebuild, son runtime) |
| Cambié `API_BASE_URL` y no pasó nada | Confundiste con `VITE_API_BASE_URL` de build time (no se usa aquí) | Verifica que `env.js` se regeneró: `docker compose exec web cat /usr/share/nginx/html/env.js` |
| Refrescar `/executions` da 404 | nginx del contenedor `web` sin `try_files` a `index.html` | No debería pasar con la config incluida — revisa que no se haya sobreescrito `apps/web/docker/nginx.conf` |
| Build de `web` falla en `npm ci` | `package-lock.json` desincronizado con algún `package.json` de los workspaces | Corre `npm install` en la raíz localmente primero, commitea el lockfile actualizado |
