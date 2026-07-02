"""Entidad Execution: una ejecucion de un proceso ETL."""
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.execution_status import ExecutionStatus


@dataclass(frozen=True)
class Execution:
    etl_name: str
    start_time: datetime
    status: ExecutionStatus | None
    raw_status: str
    execution_id: str | None = None
    etl_version: str | None = None
    execution_type: str | None = None
    source_file: str | None = None
    end_time: datetime | None = None
    duration_seconds: int | None = None
    records_extracted: int = 0
    records_loaded: int = 0
    records_rejected: int = 0
    error_message: str | None = None
    error_stacktrace: str | None = None
    request_id: str | None = None
    created_at: datetime | None = None

    @property
    def effective_duration_seconds(self) -> int | None:
        """Duracion registrada, o calculada desde start/end si falta (RF-006)."""
        if self.duration_seconds is not None:
            return self.duration_seconds
        if self.end_time is not None:
            delta = self.end_time - self.start_time
            return max(int(delta.total_seconds()), 0)
        return None

    @property
    def is_failed(self) -> bool:
        return self.status is ExecutionStatus.FAILED

    @property
    def is_running(self) -> bool:
        return self.status is ExecutionStatus.RUNNING
