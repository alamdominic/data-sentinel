"""Tests de casos de uso de ejecuciones."""
import pytest

from app.application.use_cases.etl_scope import EtlScopeResolver
from app.application.use_cases.get_execution_detail_use_case import GetExecutionDetailUseCase
from app.application.use_cases.list_executions_use_case import ListExecutionsUseCase
from app.core.errors import NotFoundError, ValidationAppError
from app.domain.repositories.queries import ExecutionFilters, PageSpec, SortSpec
from app.domain.value_objects.execution_status import ExecutionStatus
from tests.conftest import FakeEtlRegistryRepository, make_etl, make_execution


class TestEtlScopeResolver:
    def test_resolves_all_active(self):
        registry = FakeEtlRegistryRepository(
            etls=[make_etl(), make_etl(etl_id=2, etl_name="etl_clientes", table_name="etl_clientes")]
        )
        assert len(EtlScopeResolver(registry).resolve()) == 2

    def test_excludes_inactive(self):
        registry = FakeEtlRegistryRepository(
            etls=[make_etl(), make_etl(etl_id=2, etl_name="etl_off", table_name="etl_off", is_active=False)]
        )
        names = [etl.etl_name for etl in EtlScopeResolver(registry).resolve()]
        assert names == ["etl_cobranza"]

    def test_filters_by_environment_and_server(self):
        registry = FakeEtlRegistryRepository(
            etls=[
                make_etl(),
                make_etl(etl_id=2, etl_name="etl_qa", table_name="etl_qa", environment="qa"),
            ]
        )
        result = EtlScopeResolver(registry).resolve(environment="qa")
        assert [etl.etl_name for etl in result] == ["etl_qa"]

    def test_single_etl_by_name(self, registry_repo):
        result = EtlScopeResolver(registry_repo).resolve(etl_name="etl_cobranza")
        assert len(result) == 1

    def test_unknown_etl_raises_not_found(self, registry_repo):
        with pytest.raises(NotFoundError):
            EtlScopeResolver(registry_repo).resolve(etl_name="etl_fantasma")

    def test_inactive_etl_rejected(self):
        registry = FakeEtlRegistryRepository(etls=[make_etl(is_active=False)])
        with pytest.raises(ValidationAppError):
            EtlScopeResolver(registry).resolve(etl_name="etl_cobranza")


class TestListExecutionsUseCase:
    def build(self, execution_repo, registry_repo):
        return ListExecutionsUseCase(execution_repo, EtlScopeResolver(registry_repo))

    def test_paginated_result(self, execution_repo, registry_repo):
        execution_repo.executions = [
            make_execution(execution_id=f"exec-{i}") for i in range(30)
        ]
        result = self.build(execution_repo, registry_repo).execute(
            ExecutionFilters(), SortSpec(), PageSpec(page=2, limit=10)
        )
        assert result.page == 2
        assert result.total == 30
        assert result.total_pages == 3
        assert len(result.items) == 10
        assert result.items[0].execution_id == "exec-10"

    def test_empty_registry_returns_empty_page(self, execution_repo):
        use_case = self.build(execution_repo, FakeEtlRegistryRepository())
        result = use_case.execute(ExecutionFilters(), SortSpec(), PageSpec())
        assert result.total == 0
        assert result.items == []

    def test_dto_contains_composite_id_and_status(self, execution_repo, registry_repo):
        execution_repo.executions = [make_execution()]
        result = self.build(execution_repo, registry_repo).execute(
            ExecutionFilters(), SortSpec(), PageSpec()
        )
        item = result.items[0]
        assert item.id.startswith("etl_cobranza::exec-1::")
        assert item.status == "SUCCESS"

    def test_unknown_status_passthrough(self, execution_repo, registry_repo):
        execution_repo.executions = [make_execution(status=None, raw_status="WEIRD")]
        result = self.build(execution_repo, registry_repo).execute(
            ExecutionFilters(), SortSpec(), PageSpec()
        )
        assert result.items[0].status == "WEIRD"


class TestGetExecutionDetailUseCase:
    def build(self, execution_repo, registry_repo):
        return GetExecutionDetailUseCase(execution_repo, registry_repo)

    def test_returns_detail(self, execution_repo, registry_repo):
        execution = make_execution(error_message="boom", error_stacktrace="trace")
        execution_repo.executions = [execution]
        composite = f"etl_cobranza::exec-1::{execution.start_time.isoformat()}"
        detail = self.build(execution_repo, registry_repo).execute(composite)
        assert detail.error_message == "boom"
        assert detail.error_stacktrace == "trace"

    def test_invalid_id_rejected(self, execution_repo, registry_repo):
        with pytest.raises(ValidationAppError):
            self.build(execution_repo, registry_repo).execute("basura")

    def test_unknown_etl_not_found(self, execution_repo, registry_repo):
        with pytest.raises(NotFoundError):
            self.build(execution_repo, registry_repo).execute(
                "etl_fantasma::x::2026-07-01T00:00:00+00:00"
            )

    def test_missing_execution_not_found(self, execution_repo, registry_repo):
        with pytest.raises(NotFoundError):
            self.build(execution_repo, registry_repo).execute(
                "etl_cobranza::no-existe::2026-07-01T00:00:00+00:00"
            )

    def test_failed_execution_detail(self, execution_repo, registry_repo):
        execution = make_execution(
            status=ExecutionStatus.FAILED, raw_status="FAILED", error_message="ETL exploto"
        )
        execution_repo.executions = [execution]
        composite = f"etl_cobranza::exec-1::{execution.start_time.isoformat()}"
        detail = self.build(execution_repo, registry_repo).execute(composite)
        assert detail.status == "FAILED"
