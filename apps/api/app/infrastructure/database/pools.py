"""Pools de conexion PostgreSQL.

Dos pools: datos ETL (solo lectura) y metadatos (app_users, etl_registry).
Si APP_METADATA_DATABASE_URL no se define, ambos usan la misma conexion.
"""
from psycopg_pool import ConnectionPool

from app.core.settings import Settings


class DatabasePools:
    def __init__(self, settings: Settings):
        self.etl_pool = ConnectionPool(
            conninfo=settings.database_url,
            min_size=1,
            max_size=10,
            open=False,
            name="etl-readonly",
        )
        if settings.metadata_database_url == settings.database_url:
            self.metadata_pool = self.etl_pool
        else:
            self.metadata_pool = ConnectionPool(
                conninfo=settings.metadata_database_url,
                min_size=1,
                max_size=5,
                open=False,
                name="metadata",
            )

    def open(self) -> None:
        self.etl_pool.open()
        if self.metadata_pool is not self.etl_pool:
            self.metadata_pool.open()

    def close(self) -> None:
        self.etl_pool.close()
        if self.metadata_pool is not self.etl_pool:
            self.metadata_pool.close()
