"""Validacion centralizada de filtros de consulta.

Todo parametro del cliente pasa por aqui antes de llegar a los repositorios.
"""
from datetime import datetime, timezone

from app.core.errors import ValidationAppError
from app.domain.repositories.queries import ExecutionFilters
from app.domain.value_objects.execution_status import ExecutionStatus

_MAX_TEXT_FILTER_LENGTH = 200


def _parse_date(raw: str | None, field: str) -> datetime | None:
    if raw is None or raw == "":
        return None
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        raise ValidationAppError(details=[{"field": field, "issue": "Fecha invalida, use ISO 8601"}])
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_status(raw: str | None) -> ExecutionStatus | None:
    if raw is None or raw == "":
        return None
    status = ExecutionStatus.parse(raw)
    if status is None:
        raise ValidationAppError(
            details=[{"field": "status", "issue": f"Valores permitidos: {ExecutionStatus.values()}"}]
        )
    return status


def _clean_text(raw: str | None, field: str) -> str | None:
    if raw is None or raw.strip() == "":
        return None
    cleaned = raw.strip()
    if len(cleaned) > _MAX_TEXT_FILTER_LENGTH:
        raise ValidationAppError(details=[{"field": field, "issue": "Filtro demasiado largo"}])
    return cleaned


def validate_execution_filters(
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    execution_type: str | None = None,
    source_file: str | None = None,
    request_id: str | None = None,
) -> ExecutionFilters:
    start = _parse_date(start_date, "startDate")
    end = _parse_date(end_date, "endDate")
    if start and end and start > end:
        raise ValidationAppError(
            details=[{"field": "startDate", "issue": "startDate no puede ser mayor que endDate"}]
        )
    return ExecutionFilters(
        start_date=start,
        end_date=end,
        status=_parse_status(status),
        execution_type=_clean_text(execution_type, "executionType"),
        source_file=_clean_text(source_file, "sourceFile"),
        request_id=_clean_text(request_id, "requestId"),
    )
