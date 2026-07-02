"""Validacion de identificadores de tabla para consultas dinamicas.

Los nombres de tabla nunca se interpolan directo desde el cliente:
1. Deben cumplir el patron de identificador PostgreSQL simple.
2. Deben existir en etl_registry (validado en capa application).
"""
import re
from dataclasses import dataclass

_IDENTIFIER_PATTERN = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


class InvalidTableIdentifierError(ValueError):
    pass


@dataclass(frozen=True)
class TableIdentifier:
    schema_name: str
    table_name: str

    def __post_init__(self) -> None:
        for part in (self.schema_name, self.table_name):
            if not _IDENTIFIER_PATTERN.match(part):
                raise InvalidTableIdentifierError(f"Identificador invalido: {part!r}")

    @property
    def qualified(self) -> str:
        """Nombre calificado y citado, seguro para interpolar en SQL."""
        return f'"{self.schema_name}"."{self.table_name}"'
