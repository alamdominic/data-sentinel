"""Entidad User: usuario autorizado de la plataforma."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    user_id: int
    email: str
    password_hash: str
    role: str = "viewer"
    full_name: str | None = None
    is_active: bool = True
    last_login_at: datetime | None = None

    @property
    def can_login(self) -> bool:
        return self.is_active

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
