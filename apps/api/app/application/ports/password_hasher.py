"""Puerto para verificacion de contrasenas (bcrypt o Argon2 en infraestructura)."""
from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        ...

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Solo para scripts administrativos; la app nunca cambia contrasenas."""
