"""Repositorio Postgres del registro dinamico de ETLs."""
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.errors import DatabaseAppError
from app.domain.entities.registered_etl import RegisteredEtl
from app.domain.repositories.etl_registry_repository import (
    EtlRegistryRepository,
    NewEtlRegistration,
)
from app.domain.value_objects.table_identifier import TableIdentifier

_COLUMNS = (
    "etl_id, etl_name, schema_name, table_name, display_name, description, "
    "environment, server_name, is_active, created_at, updated_at"
)


def _row_to_etl(row: dict[str, Any]) -> RegisteredEtl:
    return RegisteredEtl(
        etl_id=row["etl_id"],
        etl_name=row["etl_name"],
        schema_name=row["schema_name"],
        table_name=row["table_name"],
        display_name=row.get("display_name"),
        description=row.get("description"),
        environment=row.get("environment"),
        server_name=row.get("server_name"),
        is_active=row.get("is_active", True),
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
    )


class PostgresEtlRegistryRepository(EtlRegistryRepository):
    def __init__(self, pool: ConnectionPool, etl_schema: str):
        self._pool = pool
        # El schema de metadatos tambien se valida como identificador
        self._registry_table = TableIdentifier(
            schema_name=etl_schema, table_name="etl_registry"
        ).qualified

    def _fetch_all(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(query, params)
                    if cursor.description is None:
                        return []
                    return cursor.fetchall()
        except psycopg.Error as exc:
            raise DatabaseAppError() from exc

    def list_etls(
        self,
        active_only: bool = True,
        environment: str | None = None,
        server_name: str | None = None,
    ) -> list[RegisteredEtl]:
        params: dict[str, Any] = {}
        conditions = ["TRUE"]
        if active_only:
            conditions.append("is_active = TRUE")
        if environment:
            conditions.append("environment = %(environment)s")
            params["environment"] = environment
        if server_name:
            conditions.append("server_name = %(server_name)s")
            params["server_name"] = server_name
        rows = self._fetch_all(
            f"SELECT {_COLUMNS} FROM {self._registry_table} "
            f"WHERE {' AND '.join(conditions)} ORDER BY etl_name ASC",
            params,
        )
        return [_row_to_etl(row) for row in rows]

    def get_by_name(self, etl_name: str) -> RegisteredEtl | None:
        rows = self._fetch_all(
            f"SELECT {_COLUMNS} FROM {self._registry_table} WHERE etl_name = %(etl_name)s LIMIT 1",
            {"etl_name": etl_name},
        )
        return _row_to_etl(rows[0]) if rows else None

    def get_by_table(self, schema_name: str, table_name: str) -> RegisteredEtl | None:
        rows = self._fetch_all(
            f"SELECT {_COLUMNS} FROM {self._registry_table} "
            f"WHERE schema_name = %(schema_name)s AND table_name = %(table_name)s LIMIT 1",
            {"schema_name": schema_name, "table_name": table_name},
        )
        return _row_to_etl(rows[0]) if rows else None

    def table_exists(self, schema_name: str, table_name: str) -> bool:
        rows = self._fetch_all(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema = %(schema_name)s AND table_name = %(table_name)s LIMIT 1",
            {"schema_name": schema_name, "table_name": table_name},
        )
        return bool(rows)

    def register(self, registration: NewEtlRegistration) -> RegisteredEtl:
        rows = self._fetch_all(
            f"INSERT INTO {self._registry_table} "
            "(etl_name, schema_name, table_name, display_name, description, "
            "environment, server_name, created_by) "
            "VALUES (%(etl_name)s, %(schema_name)s, %(table_name)s, %(display_name)s, "
            "%(description)s, %(environment)s, %(server_name)s, %(created_by)s) "
            f"RETURNING {_COLUMNS}",
            {
                "etl_name": registration.etl_name,
                "schema_name": registration.schema_name,
                "table_name": registration.table_name,
                "display_name": registration.display_name,
                "description": registration.description,
                "environment": registration.environment,
                "server_name": registration.server_name,
                "created_by": registration.created_by,
            },
        )
        return _row_to_etl(rows[0])

    def set_active(self, etl_id: int, is_active: bool) -> RegisteredEtl | None:
        rows = self._fetch_all(
            f"UPDATE {self._registry_table} "
            "SET is_active = %(is_active)s, updated_at = CURRENT_TIMESTAMP "
            "WHERE etl_id = %(etl_id)s "
            f"RETURNING {_COLUMNS}",
            {"etl_id": etl_id, "is_active": is_active},
        )
        return _row_to_etl(rows[0]) if rows else None
