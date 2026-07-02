"""Identificador estable de ejecucion para la API.

Las tablas ETL no tienen llave primaria obligatoria. La API construye:

    <etlName>::<key>::<startTime ISO>

donde key es execution_id, o request_id si es nulo, o created_at si ambos
son nulos (ver 02-DATABASE_CONTRACT.md seccion 10). Se usa '::' como
separador porque los timestamps ISO contienen ':' simples.
"""
from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.execution import Execution

_SEPARATOR = "::"


class InvalidExecutionKeyError(ValueError):
    pass


@dataclass(frozen=True)
class ExecutionKey:
    etl_name: str
    key: str
    start_time: datetime


def build_execution_key(execution: Execution) -> str:
    key = execution.execution_id or execution.request_id
    if not key:
        created = execution.created_at or execution.start_time
        key = created.isoformat()
    return _SEPARATOR.join([execution.etl_name, key, execution.start_time.isoformat()])


def parse_execution_key(raw: str) -> ExecutionKey:
    parts = raw.split(_SEPARATOR)
    if len(parts) != 3 or not all(parts):
        raise InvalidExecutionKeyError("Identificador de ejecucion invalido")
    etl_name, key, start_raw = parts
    try:
        start_time = datetime.fromisoformat(start_raw)
    except ValueError as exc:
        raise InvalidExecutionKeyError("Fecha de inicio invalida en identificador") from exc
    return ExecutionKey(etl_name=etl_name, key=key, start_time=start_time)
