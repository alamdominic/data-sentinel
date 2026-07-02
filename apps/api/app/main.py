"""Punto de entrada de la API DATA SENTINEL."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.interfaces.api.dependencies import build_container
from app.interfaces.api.routes import auth, dashboard, etl_registry, executions, health, statistics
from app.interfaces.errors.handlers import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = build_container()
    container.pools.open()
    app.state.container = container
    yield
    container.pools.close()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="DATA SENTINEL API",
        description="Monitoreo de ejecuciones ETL. Los datos ETL son de solo lectura.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )
    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(dashboard.router)
    # El orden importa: /api/executions/{id} usa :path, va despues del listado
    app.include_router(executions.router)
    app.include_router(statistics.router)
    app.include_router(etl_registry.router)
    return app


app = create_app()
