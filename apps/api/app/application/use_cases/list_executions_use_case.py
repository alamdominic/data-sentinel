"""Caso de uso: listado paginado de ejecuciones (RF-001..RF-004, RF-008, RF-009)."""
import math

from app.application.dto.execution_dto import PaginatedExecutionsDTO, to_summary_dto
from app.application.use_cases.etl_scope import EtlScopeResolver
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.repositories.queries import ExecutionFilters, PageSpec, SortSpec


class ListExecutionsUseCase:
    def __init__(self, executions: ExecutionRepository, scope: EtlScopeResolver):
        self._executions = executions
        self._scope = scope

    def execute(
        self,
        filters: ExecutionFilters,
        sort: SortSpec,
        page: PageSpec,
        etl_name: str | None = None,
        environment: str | None = None,
        server_name: str | None = None,
    ) -> PaginatedExecutionsDTO:
        etls = self._scope.resolve(etl_name, environment, server_name)
        if not etls:
            return PaginatedExecutionsDTO(
                items=[], page=page.page, limit=page.limit, total=0, total_pages=0
            )
        items, total = self._executions.list_executions(etls, filters, sort, page)
        return PaginatedExecutionsDTO(
            items=[to_summary_dto(execution) for execution in items],
            page=page.page,
            limit=page.limit,
            total=total,
            total_pages=math.ceil(total / page.limit) if total else 0,
        )
