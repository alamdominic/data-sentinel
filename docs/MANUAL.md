# DATA SENTINEL — Manual de instalación y uso

Guía completa para levantar la aplicación en local, desde cero. Sigue los pasos **en orden**.

---

## Cómo funciona la aplicación (panorama general)

DATA SENTINEL tiene 3 piezas que deben estar corriendo/configuradas:

```text
┌─────────────┐    HTTP     ┌──────────────┐    SQL (solo lectura)   ┌────────────┐
│  Navegador   │ ─────────► │  Frontend     │                        │            │
│  (tú)        │            │  React :5173  │                        │ PostgreSQL │
└─────────────┘            └──────┬───────┘                        │            │
                                   │ REST                            │  schema:   │
                                   ▼                                 │  etl_      │
                            ┌──────────────┐        SQL              │  execution │
                            │  Backend      │ ──────────────────────►│  _aws      │
                            │  FastAPI :8000│                        │            │
                            └──────────────┘                        └────────────┘
```

1. **PostgreSQL** guarda todo: las tablas de ejecuciones ETL (que llenan los procesos ETL, no esta app), los usuarios (`app_users`) y el registro de tablas ETL (`etl_registry`).
2. **Backend (FastAPI)** lee PostgreSQL y expone la API REST en el puerto 8000. Valida el login y arma los indicadores.
3. **Frontend (React)** es lo que ves en el navegador, en el puerto 5173. Le pide todo al backend.

La app **nunca ejecuta ETLs ni modifica datos de ejecución** — solo consulta.

---

## Requisitos previos

| Herramienta | Versión mínima | Verificar con |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| PostgreSQL | 13+ corriendo en local o accesible | `psql --version` |
| Acceso admin a PostgreSQL | usuario/contraseña con permisos de crear tablas | — |

Todos los comandos de este manual se ejecutan en **PowerShell**, desde la raíz del proyecto:

```powershell
cd C:\Users\PracticanteBI\Documents\DataSentinel
```

---

## Paso 1 — Crear las tablas en PostgreSQL

Necesitas las tablas de metadatos (`app_users` y `etl_registry`). Conéctate a tu base con un usuario administrador y ejecuta el script:

```powershell
# Reemplaza admin, etl_db con tus datos reales
psql -U admin -d etl_db -f scripts\db\01_metadata.sql
```

**Opcional (recomendado para probar):** carga datos demo — crea 2 tablas ETL de ejemplo (`etl_cobranza`, `etl_clientes`) con 14 días de ejecuciones ficticias y las registra:

```powershell
psql -U admin -d etl_db -f scripts\db\02_demo_seed.sql
```

> Si no tienes `psql` en el PATH, puedes abrir los archivos `.sql` y ejecutar su contenido desde pgAdmin / DBeaver.

---

## Paso 2 — Configurar las variables de entorno

Hay **3 archivos `.env`** (ya existen, solo edita las credenciales). Ninguno se sube a git.

### 2a. `scripts\.env` — credencial de administrador (para crear usuarios)

```dotenv
DATABASE_ADMIN_URL=postgresql://admin:TU_PASSWORD@localhost:5432/etl_db
AUTH_ALLOWED_EMAIL_DOMAIN=lazarza.com.mx
```

Formato de la URL: `postgresql://USUARIO:CONTRASEÑA@SERVIDOR:PUERTO/BASE_DE_DATOS`

### 2b. `apps\api\.env` — backend

Edita las 5 variables de conexión con tus datos reales:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_USER=admin
DB_PASSWORD=TU_PASSWORD
DB_NAME=etl_db
```

El backend arma la cadena de conexión con estas 5 variables (la contraseña se escapa automáticamente, así que puede tener `@`, `/`, `:`, etc. sin problema). `APP_METADATA_DATABASE_URL` queda vacía para usar la misma conexión en metadatos; solo llénala si tienes un usuario distinto para `app_users`/`etl_registry`. `DATABASE_URL` es una alternativa avanzada (URL completa) que, si se define, tiene prioridad sobre las 5 variables — déjala vacía salvo que la necesites.

> Para desarrollo local puedes usar el mismo usuario admin en ambas conexiones. En producción se usan usuarios separados de solo lectura (ver comentarios en `scripts/db/01_metadata.sql`).
>
> `AUTH_SECRET_KEY` ya viene generada — no la compartas ni la cambies sin motivo (cambiarla cierra todas las sesiones).

### 2c. `apps\web\.env` — frontend

Ya está listo, no requiere cambios:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

---

## Paso 3 — Instalar dependencias (solo la primera vez)

### Backend

```powershell
cd apps\api
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
cd ..\..
```

### Frontend

```powershell
npm install
```

---

## Paso 4 — Crear tu usuario y contraseña

La aplicación **no tiene registro público ni cambio de contraseña desde la web** (por diseño). Los usuarios se crean con un script local:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts\create_user.py becario.bi@lazarza.com.mx "Tu Nombre" admin
```

- Argumento 1: tu correo (debe terminar en `@lazarza.com.mx`, si no lo rechaza).
- Argumento 2: tu nombre completo, entre comillas.
- Argumento 3: rol — `admin` o `viewer` (opcional, default `viewer`).

El script te pedirá la contraseña dos veces (no se ve mientras escribes, es normal). Mínimo 8 caracteres. Al final verás:

```text
Usuario becario.bi@lazarza.com.mx creado/actualizado (role=admin).
```

> Si aparece el mensaje "DATABASE_ADMIN_URL no definida", revisa el paso 2a. En ese caso el script imprime el SQL para que lo ejecutes tú manualmente en pgAdmin.

---

## Paso 5 — Arrancar la aplicación

Necesitas **2 terminales abiertas al mismo tiempo** (una por servidor).

### Terminal 1 — Backend

```powershell
cd C:\Users\PracticanteBI\Documents\DataSentinel\apps\api
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Sabrás que funcionó cuando veas: `Uvicorn running on http://127.0.0.1:8000`

Prueba rápida: abre <http://localhost:8000/api/health> en el navegador. Debe responder `{"status":"ok","database":"up",...}`. Si dice `"database":"down"`, la conexión del paso 2b está mal.

También puedes explorar la API en <http://localhost:8000/docs> (documentación interactiva automática).

### Terminal 2 — Frontend

```powershell
cd C:\Users\PracticanteBI\Documents\DataSentinel
npm run dev:web
```

Sabrás que funcionó cuando veas: `Local: http://localhost:5173/`

### Entrar

1. Abre <http://localhost:5173> en el navegador.
2. Ingresa el correo y contraseña que creaste en el paso 4.
3. Deberías ver el Dashboard con los datos demo (si cargaste el seed).

---

## Uso diario (una vez instalado)

```powershell
# Terminal 1
cd apps\api; .\.venv\Scripts\uvicorn app.main:app --reload --port 8000

# Terminal 2
npm run dev:web
```

Para detener cualquiera: `Ctrl+C` en su terminal.

---

## Pantallas de la aplicación

| Pantalla | Qué hace |
|---|---|
| **Dashboard** | Indicadores generales: totales, exitosos/fallidos/en ejecución, tiempo promedio, última ejecución, último error, tendencias, ejecuciones recientes. Filtrable por ETL, fechas, estado, ambiente y servidor. |
| **Ejecuciones** | Tabla paginada de todas las ejecuciones. Filtros básicos y avanzados (tipo, archivo origen, request ID). Clic en una fila abre el detalle. Columnas ordenables. |
| **Detalle** | Todo de una ejecución: tiempos, registros procesados, mensaje de error y stacktrace (colapsado). |
| **Historial** | Todas las ejecuciones anteriores de un ETL específico. |
| **Estadísticas** | Promedios, máximos, mínimos, errores, tendencias semanal y mensual, resumen por ETL. |
| **Administración** | Registrar nuevas tablas ETL y activar/desactivar las existentes. |

### Registrar un nuevo ETL (sin tocar código)

Cuando exista una tabla nueva en el schema `etl_execution_aws` (por ejemplo `etl_facturacion`):

1. Ve a **Administración**.
2. Llena "Nombre ETL" y "Tabla" (normalmente iguales: `etl_facturacion`).
3. Opcional: nombre visible, ambiente, servidor, descripción.
4. Clic en **Registrar ETL**.

El sistema valida que la tabla exista físicamente y la incluye de inmediato en dashboard, consultas y estadísticas. Sin redeploy.

---

## Gestión de usuarios y contraseñas

Todo se hace con scripts locales (rol del ingeniero de datos). La web nunca gestiona credenciales.

| Acción | Comando |
|---|---|
| Crear usuario | `.\apps\api\.venv\Scripts\python.exe scripts\create_user.py correo@lazarza.com.mx "Nombre" viewer` |
| Cambiar contraseña (elegida) | `.\apps\api\.venv\Scripts\python.exe scripts\change_password.py correo@lazarza.com.mx` |
| Cambiar contraseña (aleatoria) | `.\apps\api\.venv\Scripts\python.exe scripts\change_password.py correo@lazarza.com.mx --generate` |
| Desactivar usuario | SQL: `UPDATE etl_execution_aws.app_users SET is_active = FALSE WHERE email = 'correo@lazarza.com.mx';` |

Las contraseñas se guardan hasheadas con bcrypt: **no se pueden recuperar, solo resetear**. La opción `--generate` crea una aleatoria de 16 caracteres y la muestra una sola vez.

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `/api/health` dice `"database":"down"` | Credenciales mal en `apps\api\.env` | Verifica usuario/contraseña/puerto/nombre de base |
| Login dice "Credenciales invalidas" | Usuario no existe, contraseña mal, o usuario inactivo | Re-crea con `create_user.py` (hace upsert) |
| Login dice "dominio institucional" | El correo no termina en `@lazarza.com.mx` | Usa correo institucional |
| Frontend muestra "No se pudo conectar con el servidor" | Backend apagado | Arranca la Terminal 1 |
| Dashboard vacío | No hay ETLs registrados o sin ejecuciones en el rango (default: últimos 30 días) | Carga el seed demo o registra tus tablas en Administración |
| `psql` no se reconoce | PostgreSQL no está en el PATH | Usa pgAdmin/DBeaver para ejecutar los `.sql` |
| Error al instalar deps de Python | venv no activado o Python < 3.11 | Verifica `python --version` |
| Puerto 8000 o 5173 ocupado | Otra app lo usa | Cambia `API_PORT` en `apps\api\.env` (y `VITE_API_BASE_URL` en `apps\web\.env`) |

---

## Correr los tests (verificación)

```powershell
# Backend (84 tests)
cd apps\api; .\.venv\Scripts\python.exe -m pytest --cov; cd ..\..

# Frontend (28 tests)
npm run test:web
```
