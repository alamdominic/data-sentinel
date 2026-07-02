"""Regla de dominio: solo correos del dominio institucional."""
import re
from dataclasses import dataclass

_EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class InvalidEmailError(ValueError):
    pass


class ForbiddenDomainError(ValueError):
    pass


@dataclass(frozen=True)
class InstitutionalEmail:
    value: str
    allowed_domain: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        object.__setattr__(self, "value", normalized)
        if not _EMAIL_PATTERN.match(normalized):
            raise InvalidEmailError("Formato de correo invalido")
        if not normalized.endswith(f"@{self.allowed_domain.lower()}"):
            raise ForbiddenDomainError("El correo no pertenece al dominio institucional")
