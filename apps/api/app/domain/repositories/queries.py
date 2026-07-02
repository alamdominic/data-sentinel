"""Objetos de consulta compartidos por los contratos de repositorio."""
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.value_objects.execution_status import ExecutionStatus


@dataclass(frozen=True)
class ExecutionFilters:
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: ExecutionStatus | None = None
    execution_type: str | None = None
    source_file: str | None = None
    request_id: str | None = None


@dataclass(frozen=True)
class SortSpec:
    column: str = "start_time"
    direction: str = "desc"


@dataclass(frozen=True)
class PageSpec:
    page: int = 1
    limit: int = 25

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


@dataclass(frozen=True)
class TrendPoint:
    period: str
    executions: int
    failures: int
    average_duration_seconds: float | None = None


@dataclass(frozen=True)
class EtlAggregate:
    etl_name: str
    execution_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    running_count: int = 0
    warning_count: int = 0
    cancelled_count: int = 0
    average_duration_seconds: float | None = None
    max_duration_seconds: int | None = None
    min_duration_seconds: int | None = None
    last_execution_at: datetime | None = None


@dataclass(frozen=True)
class StatusDistribution:
    counts: dict[str, int] = field(default_factory=dict)
