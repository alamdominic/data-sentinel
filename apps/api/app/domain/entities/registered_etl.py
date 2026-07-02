"""Entidad RegisteredEtl: tabla ETL registrada dinamicamente en etl_registry."""
from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.table_identifier import TableIdentifier


@dataclass(frozen=True)
class RegisteredEtl:
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

    @property
    def table(self) -> TableIdentifier:
        """Identificador validado, seguro para construir SQL."""
        return TableIdentifier(schema_name=self.schema_name, table_name=self.table_name)

    @property
    def label(self) -> str:
        return self.display_name or self.etl_name
