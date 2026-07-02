"""GET /api/statistics - indicadores historicos."""
from fastapi import APIRouter, Depends, Query

from app.application.dto.auth_dto import AuthUserDTO
from app.application.dto.statistics_dto import StatisticsDTO
from app.application.validators.filter_validator import validate_execution_filters
from app.interfaces.api.dependencies import Container, get_container, get_current_user

router = APIRouter(prefix="/api", tags=["statistics"])


@router.get("/statistics", response_model=StatisticsDTO, response_model_by_alias=True)
def get_statistics(
    etl: str | None = Query(default=None),
    start_date: str | None = Query(default=None, alias="startDate"),
    end_date: str | None = Query(default=None, alias="endDate"),
    environment: str | None = Query(default=None),
    server: str | None = Query(default=None),
    container: Container = Depends(get_container),
    _user: AuthUserDTO = Depends(get_current_user),
) -> StatisticsDTO:
    filters = validate_execution_filters(start_date=start_date, end_date=end_date)
    return container.get_statistics_use_case.execute(
        filters, etl_name=etl, environment=environment, server_name=server
    )
