"""Rutas de consulta de ejecuciones."""
from fastapi import APIRouter, Depends, Query

from app.application.dto.auth_dto import AuthUserDTO
from app.application.dto.execution_dto import ExecutionDetailDTO, PaginatedExecutionsDTO
from app.application.validators.filter_validator import validate_execution_filters
from app.application.validators.pagination_validator import validate_pagination
from app.application.validators.sort_validator import validate_sort
from app.interfaces.api.dependencies import Container, get_container, get_current_user

router = APIRouter(prefix="/api/executions", tags=["executions"])


@router.get("", response_model=PaginatedExecutionsDTO, response_model_by_alias=True)
def list_executions(
    etl: str | None = Query(default=None),
    start_date: str | None = Query(default=None, alias="startDate"),
    end_date: str | None = Query(default=None, alias="endDate"),
    status: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    server: str | None = Query(default=None),
    execution_type: str | None = Query(default=None, alias="executionType"),
    source_file: str | None = Query(default=None, alias="sourceFile"),
    request_id: str | None = Query(default=None, alias="requestId"),
    sort_by: str | None = Query(default=None, alias="sortBy"),
    sort_dir: str | None = Query(default=None, alias="sortDir"),
    page: int | None = Query(default=None),
    limit: int | None = Query(default=None),
    container: Container = Depends(get_container),
    _user: AuthUserDTO = Depends(get_current_user),
) -> PaginatedExecutionsDTO:
    filters = validate_execution_filters(
        start_date=start_date,
        end_date=end_date,
        status=status,
        execution_type=execution_type,
        source_file=source_file,
        request_id=request_id,
    )
    sort = validate_sort(sort_by, sort_dir)
    page_spec = validate_pagination(page, limit)
    return container.list_executions_use_case.execute(
        filters, sort, page_spec, etl_name=etl, environment=environment, server_name=server
    )


@router.get("/{execution_id:path}", response_model=ExecutionDetailDTO, response_model_by_alias=True)
def get_execution_detail(
    execution_id: str,
    container: Container = Depends(get_container),
    _user: AuthUserDTO = Depends(get_current_user),
) -> ExecutionDetailDTO:
    """Detalle completo. El id es el identificador compuesto de la API."""
    return container.get_execution_detail_use_case.execute(execution_id)
