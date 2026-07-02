"""Validacion de alta de tablas ETL en el registro dinamico."""
from app.core.errors import ValidationAppError
from app.domain.repositories.etl_registry_repository import NewEtlRegistration
from app.domain.value_objects.table_identifier import (
    InvalidTableIdentifierError,
    TableIdentifier,
)

_MAX_NAME_LENGTH = 120
_MAX_DISPLAY_LENGTH = 150


def validate_registration(
    etl_name: str,
    table_name: str,
    allowed_schema: str,
    schema_name: str | None = None,
    display_name: str | None = None,
    description: str | None = None,
    environment: str | None = None,
    server_name: str | None = None,
    created_by: int | None = None,
) -> NewEtlRegistration:
    details = []
    cleaned_name = (etl_name or "").strip()
    cleaned_table = (table_name or "").strip().lower()
    cleaned_schema = (schema_name or allowed_schema).strip().lower()

    if not cleaned_name or len(cleaned_name) > _MAX_NAME_LENGTH:
        details.append({"field": "etlName", "issue": "Nombre requerido, maximo 120 caracteres"})
    if cleaned_schema != allowed_schema:
        details.append({"field": "schemaName", "issue": f"Solo se permite el schema {allowed_schema}"})
    try:
        TableIdentifier(schema_name=cleaned_schema or allowed_schema, table_name=cleaned_table or "_")
    except InvalidTableIdentifierError:
        details.append({"field": "tableName", "issue": "Nombre de tabla invalido"})
    if display_name and len(display_name) > _MAX_DISPLAY_LENGTH:
        details.append({"field": "displayName", "issue": "Maximo 150 caracteres"})
    if details:
        raise ValidationAppError(details=details)

    return NewEtlRegistration(
        etl_name=cleaned_name,
        schema_name=cleaned_schema,
        table_name=cleaned_table,
        display_name=(display_name or "").strip() or None,
        description=(description or "").strip() or None,
        environment=(environment or "").strip() or None,
        server_name=(server_name or "").strip() or None,
        created_by=created_by,
    )
