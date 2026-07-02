"""GET /api/dashboard - indicadores generales."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query

from app.application.dto.auth_dto import AuthUserDTO
from app.application.dto.dashboard_dto import DashboardDTO
from app.application.validators.filter_validator import validate_execution_filters
from app.interfaces.api.dependencies import Container, get_container, get_current_user

router = APIRouter(prefix="/api", tags=["dashboard"])

# Ventana por defecto cuando el cliente no envia rango de fechas
DEFAULT_WINDOW_DAYS = 30


@router.get("/dashboard", response_model=DashboardDTO, response_model_by_alias=True)
def get_dashboard(
    etl: str | None = Query(default=None),
    start_date: str | None = Query(default=None, alias="startDate"),
    end_date: str | None = Query(default=None, alias="endDate"),
    status: str | None = Query(default=None),
    environment: str | None = Query(default=None),
    server: str | None = Query(default=None),
    container: Container = Depends(get_container),
    _user: AuthUserDTO = Depends(get_current_user),
) -> DashboardDTO:
    if not start_date and not end_date:
        window_start = datetime.now(timezone.utc) - timedelta(days=DEFAULT_WINDOW_DAYS)
        start_date = window_start.isoformat()
    filters = validate_execution_filters(start_date=start_date, end_date=end_date, status=status)
    return container.get_dashboard_use_case.execute(
        filters, etl_name=etl, environment=environment, server_name=server
    )
