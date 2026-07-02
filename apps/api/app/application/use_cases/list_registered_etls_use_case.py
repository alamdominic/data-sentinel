"""Caso de uso: listar tablas ETL registradas."""
from app.application.dto.etl_registry_dto import EtlRegistryDTO, to_etl_registry_dto
from app.domain.repositories.etl_registry_repository import EtlRegistryRepository


class ListRegisteredEtlsUseCase:
    def __init__(self, registry: EtlRegistryRepository):
        self._registry = registry

    def execute(self, include_inactive: bool = False) -> list[EtlRegistryDTO]:
        etls = self._registry.list_etls(active_only=not include_inactive)
        return [to_etl_registry_dto(etl) for etl in etls]
