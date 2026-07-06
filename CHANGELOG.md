# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

## [1.0.0] - 2026-07-03

Primera versión estable de **DATA SENTINEL**: panel web de solo lectura para monitorear las ejecuciones de los procesos ETL sin necesidad de acceder a AWS.

### Added

#### Frontend (React 18 + TypeScript + Vite)

- Pantalla de **login** con autenticación JWT (dominio restringido `@lazarza.com.mx`).
- **Dashboard** con totales, ejecuciones exitosas/fallidas/en ejecución, tiempo promedio, última ejecución, último error, tendencias y ejecuciones recientes. Filtrable por ETL, fechas, estado, ambiente y servidor.
- Vista de **Ejecuciones**: tabla paginada y ordenable con filtros básicos y avanzados (tipo, archivo origen, request ID).
- Vista de **Detalle** de ejecución: tiempos, registros procesados, mensaje de error y stacktrace.
- Vista de **Historial** de ejecuciones previas por ETL.
- Vista de **Estadísticas**: promedios, máximos, mínimos, errores y tendencias semanal/mensual.
- Vista de **Administración**: registro de nuevas tablas ETL y activación/desactivación de las existentes sin redeploy.
- UI construida con TailwindCSS, TanStack Query, Recharts y Lucide.

#### Backend (FastAPI + Python 3.11)

- API REST bajo `/api` con Clean Architecture y acceso a PostgreSQL vía psycopg3.
- Acceso a datos ETL en modo **solo lectura** (únicamente `SELECT` sobre el schema `etl_execution_aws`).
- Autenticación con JWT + bcrypt.
- Backend escucha solo en `127.0.0.1`; nginx como única puerta de entrada con TLS.

#### Infraestructura y despliegue

- Monorepo con npm workspaces (`apps/web`, `packages/*`).
- Despliegue en VPS (nginx + systemd) o Docker (2 contenedores + compose).
- `docker-compose.yml` para desarrollo y `docker-compose.prod.yml` para producción.

#### Documentación

- `README.md` con arquitectura, stack y guía de uso.
- Manuales en `docs/`: manual de usuario, creación de usuarios, cambio de contraseña, despliegue en Docker/VPS, configuración de Docker Hub y proxy reverso.

[Unreleased]: https://github.com/alamdominic/data-sentinel/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/alamdominic/data-sentinel/releases/tag/v1.0.0
