"""Caso de uso: detalle completo de una ejecucion (RF-005)."""
from app.application.dto.execution_dto import ExecutionDetailDTO, to_detail_dto
from app.core.errors import NotFoundError, ValidationAppError
from app.domain.repositories.etl_registry_repository import EtlRegistryRepository
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.services.execution_identity import (
    InvalidExecutionKeyError,
    parse_execution_key,
)


class GetExecutionDetailUseCase:
    def __init__(self, executions: ExecutionRepository, registry: EtlRegistryRepository):
        self._executions = executions
        self._registry = registry

    def execute(self, composite_id: str) -> ExecutionDetailDTO:
        try:
            key = parse_execution_key(composite_id)
        except InvalidExecutionKeyError as exc:
            raise ValidationAppError(details=[{"field": "id", "issue": str(exc)}])

        etl = self._registry.get_by_name(key.etl_name)
        if etl is None:
            raise NotFoundError(f"ETL no registrado: {key.etl_name}")

        execution = self._executions.find_execution(etl, key.key, key.start_time)
        if execution is None:
            raise NotFoundError("Ejecucion no encontrada")
        return to_detail_dto(execution)
