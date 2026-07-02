"""Puerto para emision y validacion de tokens de sesion."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    email: str


class TokenProvider(ABC):
    @abstractmethod
    def issue(self, payload: TokenPayload) -> str:
        ...

    @abstractmethod
    def decode(self, token: str) -> TokenPayload | None:
        """Retorna None si el token es invalido o expiro."""
