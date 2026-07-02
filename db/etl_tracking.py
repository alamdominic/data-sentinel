"""ETL execution tracker — inserts run records into the tracking table."""

import logging
import os
from datetime import datetime
from sqlalchemy import text
from app.db.config.db_config import create_db_engine

logger = logging.getLogger(__name__)


def register_execution(
    execution_type: str,
    start_time: datetime,
    end_time: datetime,
    records_extracted: int,
    records_loaded: int,
    records_rejected: int,
    status: str,
    source_file: str | None = None,
    error_message: str | None = None,
    error_stacktrace: str | None = None,
    request_id: str | None = None,
    etl_version: str | None = None,
) -> None:
    """Inserts one execution record into the ETL tracking table.

    Requires env var ETL_EXECUTION_LOG_DB (e.g. '"schema"."etl_execution_aws"').
    Silently skips if env var not set or engine unavailable.
    """
    table = os.getenv("ETL_EXECUTION_LOG_DB")
    if not table:
        logger.warning("ETL_EXECUTION_LOG_DB no definida — ejecución no registrada.")
        return

    execution_id = f"{execution_type}_{start_time.strftime('%Y%m%d_%H%M%S')}"
    duration_seconds = int((end_time - start_time).total_seconds())

    engine = create_db_engine()
    if engine is None:
        logger.error("ETL tracking: engine no disponible, ejecución no registrada.")
        return

    sql = text(f"""
        INSERT INTO {table} (
            execution_id, etl_version, execution_type, source_file,
            start_time, end_time, duration_seconds,
            records_extracted, records_loaded, records_rejected,
            status, error_message, error_stacktrace, request_id
        ) VALUES (
            :execution_id, :etl_version, :execution_type, :source_file,
            :start_time, :end_time, :duration_seconds,
            :records_extracted, :records_loaded, :records_rejected,
            :status, :error_message, :error_stacktrace, :request_id
        )
    """)

    try:
        with engine.begin() as conn:
            conn.execute(sql, {
                "execution_id": execution_id,
                "etl_version": etl_version,
                "execution_type": execution_type,
                "source_file": source_file,
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration_seconds,
                "records_extracted": records_extracted,
                "records_loaded": records_loaded,
                "records_rejected": records_rejected,
                "status": status,
                "error_message": error_message,
                "error_stacktrace": error_stacktrace,
                "request_id": request_id,
            })
        logger.info(
            "Ejecución registrada. execution_id=%s status=%s duration=%ds",
            execution_id, status, duration_seconds,
        )
    except Exception as e:
        logger.error("ETL tracking: fallo al registrar ejecución [%s]: %s", execution_id, e)
