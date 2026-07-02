"""Repositorio de ejecuciones sobre tablas ETL dinamicas.

Seguridad:
- Solo SELECT.
- Valores siempre parametrizados (%(nombre)s).
- Nombres de tabla provienen de etl_registry y pasan por TableIdentifier,
  que valida el patron de identificador y los cita. Nunca se interpola
  texto del cliente en identificadores.
"""
from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.errors import DatabaseAppError
from app.domain.entities.execution import Execution
from app.domain.entities.registered_etl import RegisteredEtl
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.repositories.queries import (
    EtlAggregate,
    ExecutionFilters,
    PageSpec,
    SortSpec,
    TrendPoint,
)
from app.domain.value_objects.execution_status import ExecutionStatus

_LIST_COLUMNS = (
    "execution_id, etl_version, execution_type, source_file, start_time, end_time, "
    "duration_seconds, records_extracted, records_loaded, records_rejected, status, "
    "error_message, request_id, created_at"
)

_DETAIL_COLUMNS = _LIST_COLUMNS.replace("error_message,", "error_message, error_stacktrace,")

# Duracion efectiva: registrada o calculada desde start/end (RF-006)
_EFFECTIVE_DURATION = (
    "COALESCE(duration_seconds, "
    "CAST(EXTRACT(EPOCH FROM (end_time - start_time)) AS INTEGER))"
)


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")


def _filters_clause(filters: ExecutionFilters, params: dict[str, Any]) -> str:
    conditions = ["TRUE"]
    if filters.start_date is not None:
        conditions.append("start_time >= %(f_start_date)s")
        params["f_start_date"] = filters.start_date
    if filters.end_date is not None:
        conditions.append("start_time <= %(f_end_date)s")
        params["f_end_date"] = filters.end_date
    if filters.status is not None:
        conditions.append("UPPER(status) = ANY(%(f_status)s)")
        params["f_status"] = ExecutionStatus.db_literals(filters.status)
    if filters.execution_type is not None:
        conditions.append("execution_type = %(f_execution_type)s")
        params["f_execution_type"] = filters.execution_type
    if filters.source_file is not None:
        conditions.append(r"source_file ILIKE %(f_source_file)s ESCAPE '\'")
        params["f_source_file"] = f"%{_escape_like(filters.source_file)}%"
    if filters.request_id is not None:
        conditions.append("request_id = %(f_request_id)s")
        params["f_request_id"] = filters.request_id
    return " AND ".join(conditions)


def _row_to_execution(row: dict[str, Any]) -> Execution:
    raw_status = str(row.get("status") or "")
    return Execution(
        etl_name=row["etl_name"],
        execution_id=row.get("execution_id"),
        etl_version=row.get("etl_version"),
        execution_type=row.get("execution_type"),
        source_file=row.get("source_file"),
        start_time=row["start_time"],
        end_time=row.get("end_time"),
        duration_seconds=row.get("duration_seconds"),
        records_extracted=row.get("records_extracted") or 0,
        records_loaded=row.get("records_loaded") or 0,
        records_rejected=row.get("records_rejected") or 0,
        status=ExecutionStatus.parse(raw_status),
        raw_status=raw_status,
        error_message=row.get("error_message"),
        error_stacktrace=row.get("error_stacktrace"),
        request_id=row.get("request_id"),
        created_at=row.get("created_at"),
    )


class PostgresExecutionRepository(ExecutionRepository):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def _fetch_all(self, query: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except psycopg.Error as exc:
            raise DatabaseAppError() from exc

    def _combined_source(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
        params: dict[str, Any],
        columns: str = _LIST_COLUMNS,
    ) -> str:
        """UNION ALL de las tablas registradas, con etl_name parametrizado."""
        where = _filters_clause(filters, params)
        subqueries = []
        for index, etl in enumerate(etls):
            name_param = f"etl_name_{index}"
            params[name_param] = etl.etl_name
            subqueries.append(
                f"SELECT %({name_param})s AS etl_name, {columns} "
                f"FROM {etl.table.qualified} WHERE {where}"
            )
        return " UNION ALL ".join(subqueries)

    def list_executions(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
        sort: SortSpec,
        page: PageSpec,
    ) -> tuple[list[Execution], int]:
        params: dict[str, Any] = {}
        source = self._combined_source(etls, filters, params)

        count_rows = self._fetch_all(
            f"SELECT COUNT(*) AS total FROM ({source}) AS combined", dict(params)
        )
        total = int(count_rows[0]["total"]) if count_rows else 0

        direction = "ASC" if sort.direction == "asc" else "DESC"
        order_column = sort.column  # ya validado contra lista blanca
        params["p_limit"] = page.limit
        params["p_offset"] = page.offset
        rows = self._fetch_all(
            f"SELECT * FROM ({source}) AS combined "
            f"ORDER BY {order_column} {direction} NULLS LAST, start_time DESC "
            f"LIMIT %(p_limit)s OFFSET %(p_offset)s",
            params,
        )
        return [_row_to_execution(row) for row in rows], total

    def find_execution(
        self,
        etl: RegisteredEtl,
        key: str,
        start_time: datetime,
    ) -> Execution | None:
        params: dict[str, Any] = {
            "etl_name": etl.etl_name,
            "key": key,
            "start_time": start_time,
        }
        key_conditions = ["execution_id = %(key)s", "request_id = %(key)s"]
        try:
            params["key_ts"] = datetime.fromisoformat(key)
            key_conditions.append("created_at = %(key_ts)s")
        except ValueError:
            pass
        rows = self._fetch_all(
            f"SELECT %(etl_name)s AS etl_name, {_DETAIL_COLUMNS} "
            f"FROM {etl.table.qualified} "
            f"WHERE start_time = %(start_time)s AND ({' OR '.join(key_conditions)}) "
            f"ORDER BY created_at DESC LIMIT 1",
            params,
        )
        return _row_to_execution(rows[0]) if rows else None

    def aggregate(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> list[EtlAggregate]:
        params: dict[str, Any] = {}
        where = _filters_clause(filters, params)
        params["st_success"] = ExecutionStatus.db_literals(ExecutionStatus.SUCCESS)
        params["st_failed"] = ExecutionStatus.db_literals(ExecutionStatus.FAILED)
        params["st_running"] = ExecutionStatus.db_literals(ExecutionStatus.RUNNING)
        params["st_warning"] = ExecutionStatus.db_literals(ExecutionStatus.WARNING)
        params["st_cancelled"] = ExecutionStatus.db_literals(ExecutionStatus.CANCELLED)
        subqueries = []
        for index, etl in enumerate(etls):
            name_param = f"etl_name_{index}"
            params[name_param] = etl.etl_name
            subqueries.append(
                f"SELECT %({name_param})s AS etl_name, "
                f"COUNT(*) AS execution_count, "
                f"COUNT(*) FILTER (WHERE UPPER(status) = ANY(%(st_success)s)) AS success_count, "
                f"COUNT(*) FILTER (WHERE UPPER(status) = ANY(%(st_failed)s)) AS failed_count, "
                f"COUNT(*) FILTER (WHERE UPPER(status) = ANY(%(st_running)s)) AS running_count, "
                f"COUNT(*) FILTER (WHERE UPPER(status) = ANY(%(st_warning)s)) AS warning_count, "
                f"COUNT(*) FILTER (WHERE UPPER(status) = ANY(%(st_cancelled)s)) AS cancelled_count, "
                f"AVG({_EFFECTIVE_DURATION})::float AS average_duration_seconds, "
                f"MAX({_EFFECTIVE_DURATION}) AS max_duration_seconds, "
                f"MIN({_EFFECTIVE_DURATION}) AS min_duration_seconds, "
                f"MAX(start_time) AS last_execution_at "
                f"FROM {etl.table.qualified} WHERE {where}"
            )
        rows = self._fetch_all(" UNION ALL ".join(subqueries), params)
        return [
            EtlAggregate(
                etl_name=row["etl_name"],
                execution_count=int(row["execution_count"] or 0),
                success_count=int(row["success_count"] or 0),
                failed_count=int(row["failed_count"] or 0),
                running_count=int(row["running_count"] or 0),
                warning_count=int(row["warning_count"] or 0),
                cancelled_count=int(row["cancelled_count"] or 0),
                average_duration_seconds=row["average_duration_seconds"],
                max_duration_seconds=row["max_duration_seconds"],
                min_duration_seconds=row["min_duration_seconds"],
                last_execution_at=row["last_execution_at"],
            )
            for row in rows
        ]

    def _first_combined(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> Execution | None:
        params: dict[str, Any] = {}
        source = self._combined_source(etls, filters, params)
        rows = self._fetch_all(
            f"SELECT * FROM ({source}) AS combined ORDER BY start_time DESC LIMIT 1", params
        )
        return _row_to_execution(rows[0]) if rows else None

    def last_execution(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> Execution | None:
        return self._first_combined(etls, filters)

    def last_error(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> Execution | None:
        failed_filters = ExecutionFilters(
            start_date=filters.start_date,
            end_date=filters.end_date,
            status=ExecutionStatus.FAILED,
            execution_type=filters.execution_type,
            source_file=filters.source_file,
            request_id=filters.request_id,
        )
        return self._first_combined(etls, failed_filters)

    def _trend(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
        granularity: str,
        period_format: str,
    ) -> list[TrendPoint]:
        params: dict[str, Any] = {}
        where = _filters_clause(filters, params)
        subqueries = [
            f"SELECT start_time, UPPER(status) AS status, "
            f"{_EFFECTIVE_DURATION} AS effective_duration "
            f"FROM {etl.table.qualified} WHERE {where}"
            for etl in etls
        ]
        source = " UNION ALL ".join(subqueries)
        params["p_period_format"] = period_format
        params["st_failed"] = ExecutionStatus.db_literals(ExecutionStatus.FAILED)
        rows = self._fetch_all(
            f"SELECT to_char(date_trunc('{granularity}', start_time), %(p_period_format)s) AS period, "
            f"COUNT(*) AS executions, "
            f"COUNT(*) FILTER (WHERE status = ANY(%(st_failed)s)) AS failures, "
            f"AVG(effective_duration)::float AS average_duration_seconds "
            f"FROM ({source}) AS combined "
            f"GROUP BY 1 ORDER BY 1",
            params,
        )
        return [
            TrendPoint(
                period=row["period"],
                executions=int(row["executions"] or 0),
                failures=int(row["failures"] or 0),
                average_duration_seconds=row["average_duration_seconds"],
            )
            for row in rows
        ]

    def daily_trend(self, etls, filters):
        return self._trend(etls, filters, "day", "YYYY-MM-DD")

    def weekly_trend(self, etls, filters):
        return self._trend(etls, filters, "week", "IYYY-\"W\"IW")

    def monthly_trend(self, etls, filters):
        return self._trend(etls, filters, "month", "YYYY-MM")
