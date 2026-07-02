"""Validacion de paginacion: page >= 1, 1 <= limit <= 100."""
from app.core.errors import ValidationAppError
from app.domain.repositories.queries import PageSpec

MIN_PAGE = 1
MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 25


def validate_pagination(page: int | None = None, limit: int | None = None) -> PageSpec:
    resolved_page = MIN_PAGE if page is None else page
    resolved_limit = DEFAULT_LIMIT if limit is None else limit
    details = []
    if resolved_page < MIN_PAGE:
        details.append({"field": "page", "issue": f"Debe ser >= {MIN_PAGE}"})
    if not (MIN_LIMIT <= resolved_limit <= MAX_LIMIT):
        details.append({"field": "limit", "issue": f"Debe estar entre {MIN_LIMIT} y {MAX_LIMIT}"})
    if details:
        raise ValidationAppError(details=details)
    return PageSpec(page=resolved_page, limit=resolved_limit)
