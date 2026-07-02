# DATA SENTINEL — Backend (API)

FastAPI, Clean Architecture. Consulta datos ETL en modo **solo lectura**; escribe únicamente en las tablas de metadatos (`app_users`, `etl_registry`).

Arquitectura detallada: [../../steps/01-ARCHITECTURE.md](../../steps/01-ARCHITECTURE.md). Contrato de datos: [../../steps/02-DATABASE_CONTRACT.md](../../steps/02-DATABASE_CONTRACT.md).

---

## Estructura de capas

```text
app/
├── domain/          Entidades, value objects, contratos de repositorio. Sin dependencias externas.
├── application/     Casos de uso, DTOs, validadores, puertos (interfaces para infra).
├── infrastructure/  Postgres (psycopg3 + pools), bcrypt, JWT. Implementa los contratos de domain/application.
├── interfaces/      Rutas FastAPI, schemas de entrada, inyección de dependencias, manejo de errores.
└── core/            Settings, logging, errores base.
```

Regla de dependencias: `interfaces` / `infrastructure` → `application` → `domain`. `domain` no importa FastAPI, psycopg ni nada externo.

---

## Desarrollo local

```powershell
cd apps\api
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
copy .env.example .env   # editar credenciales reales
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Verificar: <http://localhost:8000/api/health> → `{"status":"ok","database":"up"}`. Docs interactivas: <http://localhost:8000/docs>.

Guía completa de instalación local (incluye base de datos y usuario): [../../docs/MANUAL.md](../../docs/MANUAL.md).

---

## Variables de entorno

Ver [.env.example](.env.example). Resumen:

| Variable | Requerida | Descripción |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Sí (o `DATABASE_URL`) | Conexión a Postgres. El backend arma la URL con estas 5 variables, escapando la contraseña automáticamente (soporta `@`, `/`, `:`, etc.) |
| `DATABASE_URL` | No | Override de URL completa. Si se define, tiene prioridad sobre `DB_HOST`/... |
| `APP_METADATA_DATABASE_URL` | No | Conexión separada para `app_users`/`etl_registry`. Vacío = usa la misma conexión de arriba |
| `AUTH_SECRET_KEY` | Sí | Firma los JWT de sesión. Generar con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Cambiarla cierra todas las sesiones activas |
| `AUTH_ALLOWED_EMAIL_DOMAIN` | No (default `lazarza.com.mx`) | Dominio institucional aceptado en login |
| `AUTH_TOKEN_EXPIRE_MINUTES` | No (default `480`) | Vigencia del token de sesión |
| `PASSWORD_HASH_ALGORITHM` | No (default `bcrypt`) | Documental — el hasher activo es `BcryptPasswordHasher` |
| `ETL_SCHEMA` | No (default `etl_execution_aws`) | Schema donde viven las tablas ETL y los metadatos |
| `CORS_ALLOWED_ORIGINS` | No | Orígenes permitidos, separados por coma. **En producción debe ser el dominio real del frontend** (`https://tu-dominio.com`), nunca `*` |
| `API_ENV`, `API_PORT`, `LOG_LEVEL` | No | Configuración general |

La conexión es de **solo lectura** para datos ETL: el usuario de base de datos que uses aquí solo necesita `SELECT` sobre las tablas de `etl_execution_aws.*` y `SELECT`/`INSERT`/`UPDATE` sobre `etl_registry` y `UPDATE` acotado (`last_login_at`, `updated_at`) sobre `app_users`. Ver permisos recomendados en [../../scripts/db/01_metadata.sql](../../scripts/db/01_metadata.sql).

---

## Tests

```powershell
.\.venv\Scripts\python -m pytest --cov
```

Cobertura mínima exigida: 80% en `domain` + `application` (lógica de negocio). Los repositorios de infraestructura (SQL real) no tienen tests unitarios — se validan manualmente contra la base antes de cada cambio de consultas.

---

## Despliegue en producción

Con Docker (recomendado): [../../docs/DEPLOY_DOCKER.md](../../docs/DEPLOY_DOCKER.md) — ver [Dockerfile](Dockerfile), variables inyectadas en runtime al crear el contenedor (sin rebuild por cambio de config).

Sin contenedores, VPS con nginx + systemd: [../../docs/DEPLOY_VPS.md](../../docs/DEPLOY_VPS.md). Resumen de esta capa:

1. Clonar el repo en el servidor, crear el venv e instalar dependencias igual que en desarrollo (sin `[dev]` si no vas a correr tests ahí):
   ```bash
   cd apps/api
   python3.11 -m venv .venv
   .venv/bin/pip install -e .
   ```
2. Crear `.env` con credenciales reales y un `AUTH_SECRET_KEY` fuerte generado en el servidor (no reutilices el de desarrollo).
3. **No usar `--reload` en producción.** Correr con varios workers:
   ```bash
   .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
   ```
   El backend escucha solo en `127.0.0.1` — nginx es quien lo expone al exterior por HTTPS (ver guía VPS).
4. Gestionar el proceso con **systemd** (arranca solo, se reinicia si falla) — unit file de ejemplo en la guía VPS.
5. `CORS_ALLOWED_ORIGINS` debe apuntar al dominio real del frontend.

---

## Manejo de errores

Todas las respuestas de error siguen el formato:

```json
{"error": {"code": "VALIDATION_ERROR", "message": "...", "details": []}}
```

Nunca se exponen queries, credenciales ni stack traces al cliente (ver [core/errors.py](app/core/errors.py) e [interfaces/errors/handlers.py](app/interfaces/errors/handlers.py)).

## Gestión de usuarios y contraseñas

La API **no** expone registro ni cambio de contraseña — se administra con scripts locales:

- [../../docs/CREAR_USUARIOS.md](../../docs/CREAR_USUARIOS.md)
- [../../docs/CAMBIAR_CONTRASENA.md](../../docs/CAMBIAR_CONTRASENA.md)
