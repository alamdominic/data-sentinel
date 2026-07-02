"""DTOs del registro dinamico de ETLs."""
from datetime import datetime

from app.application.dto.common import CamelDTO
from app.domain.entities.registered_etl import RegisteredEtl


class EtlRegistryDTO(CamelDTO):
    etl_id: int
    etl_name: str
    schema_name: str
    table_name: str
    display_name: str | None = None
    description: str | None = None
    environment: str | None = None
    server_name: str | None = None
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


def to_etl_registry_dto(etl: RegisteredEtl) -> EtlRegistryDTO:
    return EtlRegistryDTO(
        etl_id=etl.etl_id,
        etl_name=etl.etl_name,
        schema_name=etl.schema_name,
        table_name=etl.table_name,
        display_name=etl.display_name,
        description=etl.description,
        environment=etl.environment,
        server_name=etl.server_name,
        is_active=etl.is_active,
        created_at=etl.created_at,
        updated_at=etl.updated_at,
    )
