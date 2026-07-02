"""Caso de uso: indicadores del dashboard (RF-007, RF-014)."""
from app.application.dto.dashboard_dto import DashboardDTO, StatusCountDTO, TrendPointDTO
from app.application.dto.execution_dto import to_summary_dto
from app.application.use_cases.etl_scope import EtlScopeResolver
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.repositories.queries import ExecutionFilters, PageSpec, SortSpec
from app.domain.value_objects.execution_status import ExecutionStatus

_RECENT_LIMIT = 10


class GetDashboardUseCase:
    def __init__(self, executions: ExecutionRepository, scope: EtlScopeResolver):
        self._executions = executions
        self._scope = scope

    def execute(
        self,
        filters: ExecutionFilters,
        etl_name: str | None = None,
        environment: str | None = None,
        server_name: str | None = None,
    ) -> DashboardDTO:
        etls = self._scope.resolve(etl_name, environment, server_name)
        if not etls:
            return DashboardDTO(
                total_etls=0,
                successful_executions=0,
                failed_executions=0,
                running_executions=0,
            )

        aggregates = self._executions.aggregate(etls, filters)
        success = sum(item.success_count for item in aggregates)
        failed = sum(item.failed_count for item in aggregates)
        running = sum(item.running_count for item in aggregates)
        warning = sum(item.warning_count for item in aggregates)
        cancelled = sum(item.cancelled_count for item in aggregates)
        total_executions = sum(item.execution_count for item in aggregates)

        durations = [
            (item.average_duration_seconds, item.execution_count)
            for item in aggregates
            if item.average_duration_seconds is not None and item.execution_count > 0
        ]
        weighted_total = sum(avg * count for avg, count in durations)
        weighted_count = sum(count for _, count in durations)
        average_duration = weighted_total / weighted_count if weighted_count else None

        last_execution = self._executions.last_execution(etls, filters)
        last_error = self._executions.last_error(etls, filters)
        trend = self._executions.daily_trend(etls, filters)

        recent, _ = self._executions.list_executions(
            etls,
            filters,
            SortSpec(column="start_time", direction="desc"),
            PageSpec(page=1, limit=_RECENT_LIMIT),
        )

        status_distribution = [
            StatusCountDTO(status=ExecutionStatus.SUCCESS.value, count=success),
            StatusCountDTO(status=ExecutionStatus.FAILED.value, count=failed),
            StatusCountDTO(status=ExecutionStatus.RUNNING.value, count=running),
            StatusCountDTO(status=ExecutionStatus.WARNING.value, count=warning),
            StatusCountDTO(status=ExecutionStatus.CANCELLED.value, count=cancelled),
        ]
        unknown = total_executions - (success + failed + running + warning + cancelled)
        if unknown > 0:
            status_distribution.append(StatusCountDTO(status="UNKNOWN", count=unknown))

        trend_dtos = [
            TrendPointDTO(
                period=point.period,
                executions=point.executions,
                failures=point.failures,
                average_duration_seconds=point.average_duration_seconds,
            )
            for point in trend
        ]

        return DashboardDTO(
            total_etls=len(etls),
            successful_executions=success,
            failed_executions=failed,
            running_executions=running,
            average_duration_seconds=average_duration,
            last_execution=to_summary_dto(last_execution) if last_execution else None,
            last_error=to_summary_dto(last_error) if last_error else None,
            execution_trend=trend_dtos,
            failure_trend=[
                TrendPointDTO(period=point.period, executions=point.failures, failures=point.failures)
                for point in trend
            ],
            status_distribution=status_distribution,
            recent_executions=[to_summary_dto(execution) for execution in recent],
        )
