"""Repositorio Postgres de usuarios autorizados.

Unica escritura permitida: last_login_at / updated_at.
"""
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.errors import DatabaseAppError
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.table_identifier import TableIdentifier

_COLUMNS = "user_id, email, password_hash, full_name, role, is_active, last_login_at"


def _row_to_user(row: dict[str, Any]) -> User:
    return User(
        user_id=row["user_id"],
        email=row["email"],
        password_hash=row["password_hash"],
        full_name=row.get("full_name"),
        role=row.get("role") or "viewer",
        is_active=row.get("is_active", True),
        last_login_at=row.get("last_login_at"),
    )


class PostgresUserRepository(UserRepository):
    def __init__(self, pool: ConnectionPool, etl_schema: str):
        self._pool = pool
        self._users_table = TableIdentifier(
            schema_name=etl_schema, table_name="app_users"
        ).qualified

    def _execute(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(query, params)
                    if cursor.description is None:
                        return []
                    return cursor.fetchall()
        except psycopg.Error as exc:
            raise DatabaseAppError() from exc

    def get_active_by_email(self, email: str) -> User | None:
        rows = self._execute(
            f"SELECT {_COLUMNS} FROM {self._users_table} "
            "WHERE lower(email) = lower(%(email)s) AND is_active = TRUE LIMIT 1",
            {"email": email},
        )
        return _row_to_user(rows[0]) if rows else None

    def get_by_id(self, user_id: int) -> User | None:
        rows = self._execute(
            f"SELECT {_COLUMNS} FROM {self._users_table} WHERE user_id = %(user_id)s LIMIT 1",
            {"user_id": user_id},
        )
        return _row_to_user(rows[0]) if rows else None

    def record_login(self, user_id: int) -> None:
        self._execute(
            f"UPDATE {self._users_table} "
            "SET last_login_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP "
            "WHERE user_id = %(user_id)s",
            {"user_id": user_id},
        )
