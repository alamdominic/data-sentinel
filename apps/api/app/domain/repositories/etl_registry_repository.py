"""Contrato de acceso al registro dinamico de tablas ETL."""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities.registered_etl import RegisteredEtl


@dataclass(frozen=True)
class NewEtlRegistration:
    etl_name: str
    schema_name: str
    table_name: str
    display_name: str | None = None
    description: str | None = None
    environment: str | None = None
    server_name: str | None = None
    created_by: int | None = None


class EtlRegistryRepository(ABC):
    @abstractmethod
    def list_etls(
        self,
        active_only: bool = True,
        environment: str | None = None,
        server_name: str | None = None,
    ) -> list[RegisteredEtl]:
        ...

    @abstractmethod
    def get_by_name(self, etl_name: str) -> RegisteredEtl | None:
        ...

    @abstractmethod
    def get_by_table(self, schema_name: str, table_name: str) -> RegisteredEtl | None:
        ...

    @abstractmethod
    def table_exists(self, schema_name: str, table_name: str) -> bool:
        """Verifica en information_schema que la tabla fisica exista."""

    @abstractmethod
    def register(self, registration: NewEtlRegistration) -> RegisteredEtl:
        ...

    @abstractmethod
    def set_active(self, etl_id: int, is_active: bool) -> RegisteredEtl | None:
        ...
