# DATA SENTINEL — Despliegue en VPS

Guía para poner en producción backend + frontend en un VPS propio.

> **Asunción:** Ubuntu 22.04/24.04 LTS con acceso `sudo`, y un dominio (ej. `datasentinel.tuempresa.com`) ya apuntando por DNS (registro A) a la IP del VPS. Si tu VPS usa otra distribución (Debian, AlmaLinux, etc.), los comandos de paquetes cambian (`apt` → `dnf`/`yum`) pero la lógica es la misma. Ajusta rutas/usuarios según tu entorno.

---

## Arquitectura de despliegue

```text
Internet (443/80)
       │
       ▼
   nginx  ──────────────► /            → archivos estáticos apps/web/dist/
       │                                  (try_files → index.html, SPA routing)
       │
       └────────────────► /api/...     → proxy_pass http://127.0.0.1:8000
                                           (FastAPI, gestionado por systemd)
                                                │
                                                ▼
                                          PostgreSQL (RDS u otro host,
                                          fuera del VPS)
```

El backend **no se expone directamente a Internet** — escucha solo en `127.0.0.1:8000`. nginx es la única puerta de entrada, con TLS.

---

## Paso 1 — Preparar el servidor

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git curl

# Node.js 20 (para compilar el frontend)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Verifica versiones: `python3.11 --version`, `node --version` (20+), `nginx -v`.

---

## Paso 2 — Subir el código

```bash
# Opción A: clonar desde tu repositorio git
git clone <url-de-tu-repo> /opt/datasentinel
cd /opt/datasentinel

# Opción B: subir con rsync/scp desde tu máquina si no usas git remoto
```

Recomendado: crear un usuario de sistema dedicado (no root) para correr la app:

```bash
sudo useradd -r -s /bin/false datasentinel
sudo chown -R datasentinel:datasentinel /opt/datasentinel
```

---

## Paso 3 — Backend

```bash
cd /opt/datasentinel/apps/api
sudo -u datasentinel python3.11 -m venv .venv
sudo -u datasentinel .venv/bin/pip install -e .
```

Crea `/opt/datasentinel/apps/api/.env` (revisa la tabla completa de variables en [../apps/api/README.md](../apps/api/README.md)):

```dotenv
DB_HOST=tu-host-postgres
DB_PORT=5432
DB_USER=ingdatos
DB_PASSWORD=tu-password-real
DB_NAME=productivo

APP_METADATA_DATABASE_URL=
DATABASE_URL=

API_ENV=production
API_PORT=8000
LOG_LEVEL=INFO

AUTH_ALLOWED_EMAIL_DOMAIN=lazarza.com.mx
PASSWORD_HASH_ALGORITHM=bcrypt
AUTH_SECRET_KEY=GENERAR_UNO_NUEVO_AQUI
AUTH_TOKEN_EXPIRE_MINUTES=480

ETL_SCHEMA=etl_execution_aws

CORS_ALLOWED_ORIGINS=https://datasentinel.tuempresa.com
```

Genera un `AUTH_SECRET_KEY` **nuevo** para producción (no reutilices el de tu máquina de desarrollo):

```bash
/opt/datasentinel/apps/api/.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Protege el archivo:

```bash
sudo chmod 600 /opt/datasentinel/apps/api/.env
sudo chown datasentinel:datasentinel /opt/datasentinel/apps/api/.env
```

### Servicio systemd

Crea `/etc/systemd/system/datasentinel-api.service`:

```ini
[Unit]
Description=DATA SENTINEL API
After=network.target

[Service]
Type=simple
User=datasentinel
Group=datasentinel
WorkingDirectory=/opt/datasentinel/apps/api
ExecStart=/opt/datasentinel/apps/api/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now datasentinel-api
sudo systemctl status datasentinel-api
curl http://127.0.0.1:8000/api/health   # {"status":"ok","database":"up"}
```

Ver logs: `sudo journalctl -u datasentinel-api -f`

---

## Paso 4 — Frontend

```bash
cd /opt/datasentinel
npm install
```

Crea `/opt/datasentinel/apps/web/.env`:

```dotenv
VITE_API_BASE_URL=https://datasentinel.tuempresa.com
```

Compila (genera archivos estáticos, no queda ningún proceso corriendo):

```bash
npm run build:web
```

Resultado en `/opt/datasentinel/apps/web/dist/`.

---

## Paso 5 — nginx

Crea `/etc/nginx/sites-available/datasentinel`:

```nginx
server {
    listen 80;
    server_name datasentinel.tuempresa.com;

    root /opt/datasentinel/apps/web/dist;
    index index.html;

    # Frontend: SPA routing — cualquier ruta no encontrada cae a index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend: proxy hacia uvicorn en localhost
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/datasentinel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Paso 6 — HTTPS (certbot)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d datasentinel.tuempresa.com
```

Certbot edita el bloque de nginx automáticamente para redirigir HTTP→HTTPS y renovar el certificado. Verifica renovación automática: `sudo certbot renew --dry-run`.

---

## Paso 7 — Verificar

```bash
curl https://datasentinel.tuempresa.com/api/health
```

Debe responder `{"status":"ok","database":"up"}`. Abre `https://datasentinel.tuempresa.com` en el navegador — deberías ver la pantalla de login.

---

## Paso 8 — Crear el primer usuario

Desde el VPS (o desde cualquier máquina con red hacia la base de datos):

```bash
cd /opt/datasentinel
sudo -u datasentinel apps/api/.venv/bin/python scripts/create_user.py becario.bi@lazarza.com.mx "Tu Nombre" admin
```

Detalle completo: [CREAR_USUARIOS.md](CREAR_USUARIOS.md).

---

## Firewall

Expón solo lo necesario — el backend nunca debe ser accesible desde fuera directamente:

```bash
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP (redirige a HTTPS)
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
```

Puerto 8000 (backend) y 5432 (Postgres) **no** deben abrirse hacia Internet — el backend solo escucha en `127.0.0.1` y Postgres vive en su propio host (RDS u otro), fuera de este firewall.

---

## Mantenimiento

### Actualizar código (nueva versión)

```bash
cd /opt/datasentinel
git pull

# Backend
cd apps/api
sudo -u datasentinel .venv/bin/pip install -e .
sudo systemctl restart datasentinel-api

# Frontend
cd ..
npm install
npm run build:web
# nginx sirve el nuevo dist/ automaticamente, sin reinicio
```

### Ver logs

```bash
sudo journalctl -u datasentinel-api -f       # backend
sudo tail -f /var/log/nginx/access.log       # accesos
sudo tail -f /var/log/nginx/error.log        # errores nginx
```

### Rotar `AUTH_SECRET_KEY`

Genera una nueva (ver Paso 3), actualiza `.env`, reinicia el servicio:

```bash
sudo systemctl restart datasentinel-api
```

Esto **cierra todas las sesiones activas** — los usuarios deberán volver a iniciar sesión.

### Registrar nuevos ETLs

No requiere tocar el servidor — se hace desde la web, en **Administración**, una vez logueado como cualquier usuario (ver limitación de roles en el README general).

---

## Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `502 Bad Gateway` en nginx | Backend caído o crasheó | `sudo systemctl status datasentinel-api`, revisar `journalctl -u datasentinel-api` |
| Frontend carga pero login falla con error de red | `VITE_API_BASE_URL` mal, o se cambió sin recompilar | Verifica el `.env` del build y **recompila** (`npm run build:web`) — Vite no lee `.env` en runtime |
| Refrescar una ruta interna (ej. `/executions`) da 404 | Falta `try_files ... /index.html` en nginx | Revisa el bloque `location /` del Paso 5 |
| `CORS error` en consola del navegador | `CORS_ALLOWED_ORIGINS` del backend no incluye el dominio | Edita `apps/api/.env`, reinicia el servicio |
| Certbot falla | DNS aún no propagado hacia el VPS | Verifica `dig datasentinel.tuempresa.com` apunte a la IP correcta antes de reintentar |
