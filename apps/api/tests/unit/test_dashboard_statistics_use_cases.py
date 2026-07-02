"""Tests de dashboard y estadisticas."""
from datetime import datetime, timezone

from app.application.use_cases.etl_scope import EtlScopeResolver
from app.application.use_cases.get_dashboard_use_case import GetDashboardUseCase
from app.application.use_cases.get_statistics_use_case import GetStatisticsUseCase
from app.domain.repositories.queries import EtlAggregate, ExecutionFilters, TrendPoint
from app.domain.value_objects.execution_status import ExecutionStatus
from tests.conftest import FakeEtlRegistryRepository, make_etl, make_execution

UTC = timezone.utc


def sample_aggregates() -> list[EtlAggregate]:
    return [
        EtlAggregate(
            etl_name="etl_cobranza",
            execution_count=10,
            success_count=7,
            failed_count=2,
            running_count=1,
            average_duration_seconds=100.0,
            max_duration_seconds=300,
            min_duration_seconds=50,
            last_execution_at=datetime(2026, 7, 1, tzinfo=UTC),
        ),
        EtlAggregate(
            etl_name="etl_clientes",
            execution_count=5,
            success_count=5,
            average_duration_seconds=200.0,
            max_duration_seconds=400,
            min_duration_seconds=20,
        ),
    ]


def two_etl_registry() -> FakeEtlRegistryRepository:
    return FakeEtlRegistryRepository(
        etls=[make_etl(), make_etl(etl_id=2, etl_name="etl_clientes", table_name="etl_clientes")]
    )


class TestGetDashboardUseCase:
    def build(self, execution_repo, registry):
        return GetDashboardUseCase(execution_repo, EtlScopeResolver(registry))

    def test_aggregated_counters(self, execution_repo):
        execution_repo.aggregates = sample_aggregates()
        execution_repo.executions = [
            make_execution(),
            make_execution(
                execution_id="exec-2", status=ExecutionStatus.FAILED, raw_status="FAILED"
            ),
        ]
        execution_repo.trend = [TrendPoint(period="2026-07-01", executions=15, failures=2)]

        dashboard = self.build(execution_repo, two_etl_registry()).execute(ExecutionFilters())

        assert dashboard.total_etls == 2
        assert dashboard.successful_executions == 12
        assert dashboard.failed_executions == 2
        assert dashboard.running_executions == 1
        # promedio ponderado: (100*10 + 200*5) / 15
        assert dashboard.average_duration_seconds == (100 * 10 + 200 * 5) / 15
        assert dashboard.last_execution is not None
        assert dashboard.last_error is not None
        assert dashboard.last_error.status == "FAILED"
        assert dashboard.execution_trend[0].executions == 15
        assert dashboard.failure_trend[0].executions == 2
        assert len(dashboard.recent_executions) == 2

    def test_status_distribution_includes_all_states(self, execution_repo):
        execution_repo.aggregates = sample_aggregates()
        dashboard = self.build(execution_repo, two_etl_registry()).execute(ExecutionFilters())
        statuses = {item.status for item in dashboard.status_distribution}
        assert {"SUCCESS", "FAILED", "RUNNING", "WARNING", "CANCELLED"} <= statuses

    def test_empty_registry(self, execution_repo):
        dashboard = self.build(execution_repo, FakeEtlRegistryRepository()).execute(
            ExecutionFilters()
        )
        assert dashboard.total_etls == 0
        assert dashboard.last_execution is None


class TestGetStatisticsUseCase:
    def build(self, execution_repo, registry):
        return GetStatisticsUseCase(execution_repo, EtlScopeResolver(registry))

    def test_global_statistics(self, execution_repo):
        execution_repo.aggregates = sample_aggregates()
        execution_repo.trend = [
            TrendPoint(period="2026-W26", executions=8, failures=1, average_duration_seconds=90.0)
        ]
        stats = self.build(execution_repo, two_etl_registry()).execute(ExecutionFilters())
        assert stats.execution_count == 15
        assert stats.error_count == 2
        assert stats.max_duration_seconds == 400
        assert stats.min_duration_seconds == 20
        assert stats.weekly_trend[0].period == "2026-W26"
        assert stats.monthly_trend[0].executions == 8
        assert len(stats.per_etl) == 2
        assert stats.per_etl[0].display_name == "Cobranza"

    def test_empty_registry_returns_zeroes(self, execution_repo):
        stats = self.build(execution_repo, FakeEtlRegistryRepository()).execute(ExecutionFilters())
        assert stats.execution_count == 0
        assert stats.per_etl == []
