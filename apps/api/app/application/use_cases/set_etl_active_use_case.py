"""Caso de uso: activar o desactivar un ETL registrado."""
from app.application.dto.etl_registry_dto import EtlRegistryDTO, to_etl_registry_dto
from app.core.errors import NotFoundError
from app.domain.repositories.etl_registry_repository import EtlRegistryRepository


class SetEtlActiveUseCase:
    def __init__(self, registry: EtlRegistryRepository):
        self._registry = registry

    def execute(self, etl_id: int, is_active: bool) -> EtlRegistryDTO:
        updated = self._registry.set_active(etl_id, is_active)
        if updated is None:
            raise NotFoundError(f"ETL con id {etl_id} no encontrado")
        return to_etl_registry_dto(updated)
