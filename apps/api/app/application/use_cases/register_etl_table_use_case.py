"""Caso de uso: registrar una nueva tabla ETL sin redeploy (RF-013).

Reglas:
- El schema debe ser el schema ETL configurado.
- La tabla fisica debe existir en PostgreSQL.
- No se permiten duplicados por nombre ni por tabla.
"""
from app.application.dto.etl_registry_dto import EtlRegistryDTO, to_etl_registry_dto
from app.application.validators.etl_registration_validator import validate_registration
from app.core.errors import ConflictError, ValidationAppError
from app.domain.repositories.etl_registry_repository import EtlRegistryRepository


class RegisterEtlTableUseCase:
    def __init__(self, registry: EtlRegistryRepository, allowed_schema: str):
        self._registry = registry
        self._allowed_schema = allowed_schema

    def execute(
        self,
        etl_name: str,
        table_name: str,
        schema_name: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        environment: str | None = None,
        server_name: str | None = None,
        created_by: int | None = None,
    ) -> EtlRegistryDTO:
        registration = validate_registration(
            etl_name=etl_name,
            table_name=table_name,
            allowed_schema=self._allowed_schema,
            schema_name=schema_name,
            display_name=display_name,
            description=description,
            environment=environment,
            server_name=server_name,
            created_by=created_by,
        )

        if self._registry.get_by_name(registration.etl_name) is not None:
            raise ConflictError(f"Ya existe un ETL registrado con nombre {registration.etl_name}")
        if self._registry.get_by_table(registration.schema_name, registration.table_name) is not None:
            raise ConflictError(
                f"La tabla {registration.schema_name}.{registration.table_name} ya esta registrada"
            )
        if not self._registry.table_exists(registration.schema_name, registration.table_name):
            raise ValidationAppError(
                details=[
                    {
                        "field": "tableName",
                        "issue": (
                            f"La tabla {registration.schema_name}.{registration.table_name} "
                            "no existe en la base de datos"
                        ),
                    }
                ]
            )

        created = self._registry.register(registration)
        return to_etl_registry_dto(created)
