"""Contrato de acceso a usuarios autorizados."""
from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_active_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    def record_login(self, user_id: int) -> None:
        """Unica escritura permitida sobre app_users: last_login_at/updated_at."""
