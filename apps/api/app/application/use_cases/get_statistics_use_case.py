"""Caso de uso: estadisticas historicas por ETL o globales."""
from app.application.dto.dashboard_dto import TrendPointDTO
from app.application.dto.statistics_dto import EtlStatisticsDTO, StatisticsDTO
from app.application.use_cases.etl_scope import EtlScopeResolver
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.repositories.queries import ExecutionFilters


class GetStatisticsUseCase:
    def __init__(self, executions: ExecutionRepository, scope: EtlScopeResolver):
        self._executions = executions
        self._scope = scope

    def execute(
        self,
        filters: ExecutionFilters,
        etl_name: str | None = None,
        environment: str | None = None,
        server_name: str | None = None,
    ) -> StatisticsDTO:
        etls = self._scope.resolve(etl_name, environment, server_name)
        if not etls:
            return StatisticsDTO()

        aggregates = self._executions.aggregate(etls, filters)
        labels = {etl.etl_name: etl.label for etl in etls}

        execution_count = sum(item.execution_count for item in aggregates)
        error_count = sum(item.failed_count for item in aggregates)
        max_durations = [
            item.max_duration_seconds for item in aggregates if item.max_duration_seconds is not None
        ]
        min_durations = [
            item.min_duration_seconds for item in aggregates if item.min_duration_seconds is not None
        ]
        weighted = [
            (item.average_duration_seconds, item.execution_count)
            for item in aggregates
            if item.average_duration_seconds is not None and item.execution_count > 0
        ]
        weighted_count = sum(count for _, count in weighted)
        average_duration = (
            sum(avg * count for avg, count in weighted) / weighted_count if weighted_count else None
        )

        def to_trend(points) -> list[TrendPointDTO]:
            return [
                TrendPointDTO(
                    period=point.period,
                    executions=point.executions,
                    failures=point.failures,
                    average_duration_seconds=point.average_duration_seconds,
                )
                for point in points
            ]

        return StatisticsDTO(
            average_duration_seconds=average_duration,
            max_duration_seconds=max(max_durations) if max_durations else None,
            min_duration_seconds=min(min_durations) if min_durations else None,
            error_count=error_count,
            execution_count=execution_count,
            weekly_trend=to_trend(self._executions.weekly_trend(etls, filters)),
            monthly_trend=to_trend(self._executions.monthly_trend(etls, filters)),
            per_etl=[
                EtlStatisticsDTO(
                    etl_name=item.etl_name,
                    display_name=labels.get(item.etl_name),
                    execution_count=item.execution_count,
                    error_count=item.failed_count,
                    average_duration_seconds=item.average_duration_seconds,
                    max_duration_seconds=item.max_duration_seconds,
                    min_duration_seconds=item.min_duration_seconds,
                )
                for item in aggregates
            ],
        )
