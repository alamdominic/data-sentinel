"""Estados permitidos de una ejecucion ETL."""
from enum import Enum


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    WARNING = "WARNING"
    CANCELLED = "CANCELLED"

    @classmethod
    def parse(cls, raw: str | None) -> "ExecutionStatus | None":
        """Normaliza un valor crudo de base de datos. Retorna None si es desconocido."""
        if raw is None:
            return None
        normalized = raw.strip().upper()
        alias = _STATUS_ALIASES.get(normalized)
        if alias is not None:
            return alias
        try:
            return cls(normalized)
        except ValueError:
            return None

    @classmethod
    def db_literals(cls, status: "ExecutionStatus") -> list[str]:
        """Valores crudos de BD equivalentes a este estado (canonico + alias).

        Usado para construir comparaciones SQL (UPPER(status) = ANY(...)) que
        reconozcan el mismo vocabulario que acepta parse().
        """
        aliases = [raw for raw, mapped in _STATUS_ALIASES.items() if mapped is status]
        return [status.value, *aliases]

    @classmethod
    def values(cls) -> list[str]:
        return [status.value for status in cls]


# Vocabulario alterno que usan algunos procesos ETL para el mismo estado logico.
# Ej.: varios ETL productores escriben status='error' en vez de 'FAILED'
# (ver etl_sad, etl_objetivo_rebanadas en produccion). Comparado en mayusculas.
_STATUS_ALIASES: dict[str, ExecutionStatus] = {
    "ERROR": ExecutionStatus.FAILED,
}
