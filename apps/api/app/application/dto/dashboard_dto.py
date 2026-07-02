"""DTOs del dashboard."""
from app.application.dto.common import CamelDTO
from app.application.dto.execution_dto import ExecutionSummaryDTO


class TrendPointDTO(CamelDTO):
    period: str
    executions: int
    failures: int
    average_duration_seconds: float | None = None


class StatusCountDTO(CamelDTO):
    status: str
    count: int


class DashboardDTO(CamelDTO):
    total_etls: int
    successful_executions: int
    failed_executions: int
    running_executions: int
    average_duration_seconds: float | None = None
    last_execution: ExecutionSummaryDTO | None = None
    last_error: ExecutionSummaryDTO | None = None
    execution_trend: list[TrendPointDTO] = []
    failure_trend: list[TrendPointDTO] = []
    status_distribution: list[StatusCountDTO] = []
    recent_executions: list[ExecutionSummaryDTO] = []
