"""Resolucion del alcance de ETLs para una consulta.

Convierte los filtros etl/environment/server en la lista de tablas
registradas y activas que se pueden consultar.
"""
from app.core.errors import NotFoundError, ValidationAppError
from app.domain.entities.registered_etl import RegisteredEtl
from app.domain.repositories.etl_registry_repository import EtlRegistryRepository


class EtlScopeResolver:
    def __init__(self, registry: EtlRegistryRepository):
        self._registry = registry

    def resolve(
        self,
        etl_name: str | None = None,
        environment: str | None = None,
        server_name: str | None = None,
    ) -> list[RegisteredEtl]:
        if etl_name:
            etl = self._registry.get_by_name(etl_name.strip())
            if etl is None:
                raise NotFoundError(f"ETL no registrado: {etl_name}")
            if not etl.is_active:
                raise ValidationAppError(
                    details=[{"field": "etl", "issue": "El ETL esta inactivo"}]
                )
            return [etl]
        return self._registry.list_etls(
            active_only=True,
            environment=(environment or "").strip() or None,
            server_name=(server_name or "").strip() or None,
        )
