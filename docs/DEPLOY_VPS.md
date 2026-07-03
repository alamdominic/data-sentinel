# DATA SENTINEL — Despliegue en VPS (Docker Hub + Compose)

Runbook real de producción: las imágenes se construyen y suben a **Docker Hub** desde tu máquina (o CI), y el VPS solo hace `pull` + `up`. **El VPS nunca clona el repositorio ni necesita Python/Node instalados** — solo Docker.

> Para entender cómo está armado el empaquetado Docker en sí (Dockerfiles, mecanismo de runtime-config del frontend, cómo probar todo en local antes de subir a Docker Hub), ver [DEPLOY_DOCKER.md](DEPLOY_DOCKER.md). Esta guía es el paso siguiente: llevar esas mismas imágenes a un VPS real.
>
> Si todavía no tienes tu máquina conectada a Docker Hub (`docker login`), hazlo primero: [DOCKER_HUB_SETUP.md](DOCKER_HUB_SETUP.md).

---

## Arquitectura

```text
Tu maquina / CI                          VPS
──────────────                          ───
docker compose build                    (sin codigo fuente, sin Python/Node)
docker compose push  ───► Docker Hub ───►  docker compose pull
                                            docker compose up -d
                                                  │
                                                  ▼
                          nginx (host, con TLS via certbot)
                                  │
                                  ▼
                          contenedor "web" (127.0.0.1:8080, no publico)
                                  │
                                  ├── estatico: frontend compilado
                                  └── /api/ ──► contenedor "api" (red interna docker)
                                                       │
                                                       ▼
                                                 PostgreSQL (fuera del VPS)
```

Ningún contenedor se publica directamente a Internet — nginx del host (paquete del sistema, no de Docker) es la única puerta de entrada, con TLS. Los contenedores solo escuchan en `127.0.0.1`.

---

## Requisito: cuenta de Docker Hub

Tu máquina debe estar autenticada (`docker login`) antes del Paso 2 — ver [DOCKER_HUB_SETUP.md](DOCKER_HUB_SETUP.md) si no lo has hecho.

Si el repositorio (`datasentinel-api` / `datasentinel-web`) es **privado**, necesitarás `docker login` también en el VPS antes de hacer `pull` (mismo procedimiento, con un Access Token). Si es público, el VPS puede hacer `pull` sin credenciales.

---

## Paso 1 — Configurar nombre de imágenes (una vez, en tu máquina)

En el `.env` de la raíz del repo (ver [.env.docker.example](../.env.docker.example)):

```dotenv
DOCKERHUB_USER=tu-usuario-dockerhub
IMAGE_TAG=latest
```

`docker-compose.yml` ya usa estos valores para nombrar las imágenes al construirlas: `tu-usuario-dockerhub/datasentinel-api:latest` y `tu-usuario-dockerhub/datasentinel-web:latest`.

> Recomendado a futuro: usar tags con versión (`v1.0.0`, o el hash corto del commit) en vez de solo `latest`, para poder hacer rollback a una versión anterior con solo cambiar `IMAGE_TAG` y volver a hacer `pull`. Con `latest` no puedes distinguir versiones ya en el VPS.

---

## Paso 2 — Build y push (en tu máquina, no en el VPS)

```bash
docker compose build
docker compose push
```

`docker compose push` sube las dos imágenes (`api` y `web`) a Docker Hub usando los nombres definidos en el Paso 1. Verifica en <https://hub.docker.com> que ambos repositorios aparezcan.

---

## Paso 3 — Preparar el VPS (solo Docker, nada de código)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# cierra sesion y vuelve a entrar para que el grupo tome efecto
docker compose version
```

El script oficial de Docker instala también el plugin `docker compose` (v2). No hace falta instalar Python ni Node.js en el VPS — ambos ya están dentro de las imágenes.

---

## Paso 4 — Copiar solo 2 archivos al VPS

No se clona el repositorio. Solo se copian `docker-compose.prod.yml` (renombrado a `docker-compose.yml` en el VPS) y `.env`:

```bash
mkdir -p /opt/datasentinel   # en el VPS, una sola vez

scp docker-compose.prod.yml usuario@tu-vps:/opt/datasentinel/docker-compose.yml
scp .env usuario@tu-vps:/opt/datasentinel/.env
```

El `.env` que copies debe tener las credenciales **reales** de producción (ver tabla de variables abajo) — no el de tu máquina de desarrollo si usa otra base de datos.

### Variables del `.env` de producción

| Variable | Notas |
|---|---|
| `DOCKERHUB_USER`, `IMAGE_TAG` | Deben coincidir con lo que pusheaste en el Paso 2 |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión real a PostgreSQL |
| `AUTH_SECRET_KEY` | **Genera una nueva para producción**, no reutilices la de desarrollo: `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` (o con Docker: `docker run --rm python:3.11-slim python -c "import secrets; print(secrets.token_urlsafe(48))"` si no tienes Python a mano) |
| `CORS_ALLOWED_ORIGINS` | El dominio público real, ej. `https://datasentinel.tuempresa.com` |
| `API_BASE_URL` | Vacío (recomendado) — mismo origen, nginx interno del contenedor `web` proxya `/api` |
| `WEB_PORT` | Puerto local (`127.0.0.1`) donde escucha el contenedor `web`; el nginx del host apunta aquí |

---

## Paso 5 — Levantar en el VPS

```bash
cd /opt/datasentinel
docker login            # solo si el repositorio de Docker Hub es privado
docker compose pull
docker compose up -d
docker compose ps
curl http://127.0.0.1:8080/api/health
```

Debe responder `{"status":"ok","database":"up"}`.

---

## Paso 6 — nginx del host + TLS

Instala nginx y certbot **en el sistema operativo del VPS** (no en Docker):

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

Crea `/etc/nginx/sites-available/datasentinel`:

```nginx
server {
    listen 80;
    server_name datasentinel.tuempresa.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Un solo `location /` alcanza — el nginx **dentro** del contenedor `web` ya resuelve el SPA routing y el proxy hacia `/api`. El nginx del host solo necesita reenviar todo el tráfico al puerto publicado.

```bash
sudo ln -s /etc/nginx/sites-available/datasentinel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

sudo certbot --nginx -d datasentinel.tuempresa.com
```

---

## Paso 7 — Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

El contenedor `web` ya está atado a `127.0.0.1` en `docker-compose.prod.yml` — no es alcanzable desde fuera del VPS aunque el firewall fallara, es una capa extra de seguridad, no la única.

---

## Paso 8 — Crear el primer usuario

Los scripts de administración (`create_user.py`, `change_password.py`) necesitan el código Python del backend — **no viven dentro de la imagen Docker** y el VPS no tiene el repo clonado. La forma más simple: correrlos **desde tu máquina local**, apuntando `DATABASE_ADMIN_URL` (en `scripts/.env`) directo a la base de datos de producción — Postgres es alcanzable por red sin importar dónde corra la app:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts\create_user.py becario.bi@lazarza.com.mx "Tu Nombre" admin
```

Detalle completo: [CREAR_USUARIOS.md](CREAR_USUARIOS.md). Esto no requiere tocar el VPS en absoluto.

---

## Mantenimiento

### Desplegar una nueva versión

```bash
# En tu maquina
docker compose build
docker compose push

# En el VPS
cd /opt/datasentinel
docker compose pull
docker compose up -d
```

### Rollback

Si usas tags con versión (no solo `latest`): cambia `IMAGE_TAG` en el `.env` del VPS al tag anterior y repite `docker compose pull && docker compose up -d`.

### Ver logs

```bash
docker compose logs -f api
docker compose logs -f web
sudo tail -f /var/log/nginx/error.log
```

### Rotar `AUTH_SECRET_KEY`

Genera una nueva, actualiza `.env` en el VPS, `docker compose up -d` (recrea el contenedor `api` con la nueva variable). Cierra todas las sesiones activas.

---

## Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `docker compose pull` falla con "not found" o "unauthorized" | Imagen no pusheada, o repo privado sin `docker login` en el VPS | Verifica en hub.docker.com que la imagen exista; haz `docker login` en el VPS |
| `502 Bad Gateway` en nginx del host | Contenedor `web` caído, o puerto/`WEB_PORT` no coincide | `docker compose ps`, `docker compose logs web` |
| `/api/health` responde `"database":"down"` | Credenciales o red hacia PostgreSQL mal en el `.env` del VPS | Revisa `DB_HOST`/`DB_USER`/`DB_PASSWORD`; prueba conexión manual |
| Cambié `.env` en el VPS y no pasó nada | Falta recrear los contenedores | `docker compose up -d` (no hace falta rebuild, son variables de runtime) |
| `create_user.py` no conecta | `DATABASE_ADMIN_URL` en `scripts/.env` mal, o el VPS/tu red bloquea el puerto de Postgres | Verifica que puedas alcanzar la base desde donde corras el script |
| Certbot falla | DNS del dominio aún no apunta al VPS | `dig datasentinel.tuempresa.com`, reintenta cuando propague |
