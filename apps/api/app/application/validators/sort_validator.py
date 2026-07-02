"""Ordenamiento por lista blanca. Nunca se ordena por texto del cliente."""
from app.core.errors import ValidationAppError
from app.domain.repositories.queries import SortSpec

# Mapeo camelCase (API) -> columna interna permitida
SORTABLE_COLUMNS: dict[str, str] = {
    "etlName": "etl_name",
    "startTime": "start_time",
    "endTime": "end_time",
    "durationSeconds": "duration_seconds",
    "status": "status",
    "recordsExtracted": "records_extracted",
    "recordsLoaded": "records_loaded",
    "recordsRejected": "records_rejected",
    "createdAt": "created_at",
}

ALLOWED_DIRECTIONS = {"asc", "desc"}

DEFAULT_SORT = SortSpec(column="start_time", direction="desc")


def validate_sort(sort_by: str | None = None, sort_dir: str | None = None) -> SortSpec:
    if sort_by is None or sort_by == "":
        column = DEFAULT_SORT.column
    else:
        column = SORTABLE_COLUMNS.get(sort_by, "")
        if not column:
            raise ValidationAppError(
                details=[{"field": "sortBy", "issue": f"Columnas permitidas: {sorted(SORTABLE_COLUMNS)}"}]
            )
    direction = (sort_dir or DEFAULT_SORT.direction).lower()
    if direction not in ALLOWED_DIRECTIONS:
        raise ValidationAppError(
            details=[{"field": "sortDir", "issue": "Direcciones permitidas: asc, desc"}]
        )
    return SortSpec(column=column, direction=direction)
