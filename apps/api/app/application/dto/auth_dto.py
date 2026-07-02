"""DTOs de autenticacion. Nunca incluyen password_hash."""
from datetime import datetime

from app.application.dto.common import CamelDTO
from app.domain.entities.user import User


class AuthUserDTO(CamelDTO):
    user_id: int
    email: str
    full_name: str | None = None
    role: str = "viewer"
    is_active: bool = True
    last_login_at: datetime | None = None


class LoginResultDTO(CamelDTO):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserDTO


def to_auth_user_dto(user: User) -> AuthUserDTO:
    return AuthUserDTO(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
    )
