"""DTOs de ejecuciones ETL."""
from datetime import datetime

from app.application.dto.common import CamelDTO
from app.domain.entities.execution import Execution
from app.domain.services.execution_identity import build_execution_key


class ExecutionSummaryDTO(CamelDTO):
    id: str
    etl_name: str
    execution_id: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: int | None = None
    status: str
    records_extracted: int = 0
    records_loaded: int = 0
    records_rejected: int = 0
    execution_type: str | None = None
    etl_version: str | None = None
    source_file: str | None = None


class ExecutionDetailDTO(CamelDTO):
    id: str
    etl_name: str
    execution_id: str | None = None
    etl_version: str | None = None
    execution_type: str | None = None
    source_file: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    duration_seconds: int | None = None
    records_extracted: int = 0
    records_loaded: int = 0
    records_rejected: int = 0
    status: str
    error_message: str | None = None
    error_stacktrace: str | None = None
    request_id: str | None = None
    created_at: datetime | None = None


class PaginatedExecutionsDTO(CamelDTO):
    items: list[ExecutionSummaryDTO]
    page: int
    limit: int
    total: int
    total_pages: int


def _display_status(execution: Execution) -> str:
    return execution.status.value if execution.status else execution.raw_status


def to_summary_dto(execution: Execution) -> ExecutionSummaryDTO:
    return ExecutionSummaryDTO(
        id=build_execution_key(execution),
        etl_name=execution.etl_name,
        execution_id=execution.execution_id,
        start_time=execution.start_time,
        end_time=execution.end_time,
        duration_seconds=execution.effective_duration_seconds,
        status=_display_status(execution),
        records_extracted=execution.records_extracted,
        records_loaded=execution.records_loaded,
        records_rejected=execution.records_rejected,
        execution_type=execution.execution_type,
        etl_version=execution.etl_version,
        source_file=execution.source_file,
    )


def to_detail_dto(execution: Execution) -> ExecutionDetailDTO:
    return ExecutionDetailDTO(
        id=build_execution_key(execution),
        etl_name=execution.etl_name,
        execution_id=execution.execution_id,
        etl_version=execution.etl_version,
        execution_type=execution.execution_type,
        source_file=execution.source_file,
        start_time=execution.start_time,
        end_time=execution.end_time,
        duration_seconds=execution.effective_duration_seconds,
        records_extracted=execution.records_extracted,
        records_loaded=execution.records_loaded,
        records_rejected=execution.records_rejected,
        status=_display_status(execution),
        error_message=execution.error_message,
        error_stacktrace=execution.error_stacktrace,
        request_id=execution.request_id,
        created_at=execution.created_at,
    )
