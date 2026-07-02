"""DTOs de estadisticas historicas."""
from app.application.dto.common import CamelDTO
from app.application.dto.dashboard_dto import TrendPointDTO


class EtlStatisticsDTO(CamelDTO):
    etl_name: str
    display_name: str | None = None
    execution_count: int = 0
    error_count: int = 0
    average_duration_seconds: float | None = None
    max_duration_seconds: int | None = None
    min_duration_seconds: int | None = None


class StatisticsDTO(CamelDTO):
    average_duration_seconds: float | None = None
    max_duration_seconds: int | None = None
    min_duration_seconds: int | None = None
    error_count: int = 0
    execution_count: int = 0
    weekly_trend: list[TrendPointDTO] = []
    monthly_trend: list[TrendPointDTO] = []
    per_etl: list[EtlStatisticsDTO] = []
