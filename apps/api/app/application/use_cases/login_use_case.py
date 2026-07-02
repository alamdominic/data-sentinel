"""Caso de uso: login con correo institucional (RF-011, RF-012)."""
from app.application.dto.auth_dto import LoginResultDTO, to_auth_user_dto
from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_provider import TokenPayload, TokenProvider
from app.core.errors import UnauthorizedError
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.institutional_email import (
    ForbiddenDomainError,
    InstitutionalEmail,
    InvalidEmailError,
)

_GENERIC_MESSAGE = "Credenciales invalidas"


class LoginUseCase:
    def __init__(
        self,
        users: UserRepository,
        hasher: PasswordHasher,
        tokens: TokenProvider,
        allowed_domain: str,
    ):
        self._users = users
        self._hasher = hasher
        self._tokens = tokens
        self._allowed_domain = allowed_domain

    def execute(self, email: str, password: str) -> LoginResultDTO:
        try:
            institutional = InstitutionalEmail(value=email, allowed_domain=self._allowed_domain)
        except ForbiddenDomainError:
            raise UnauthorizedError("El correo no pertenece al dominio institucional")
        except InvalidEmailError:
            raise UnauthorizedError(_GENERIC_MESSAGE)

        user = self._users.get_active_by_email(institutional.value)
        if user is None or not user.can_login:
            raise UnauthorizedError(_GENERIC_MESSAGE)
        if not password or not self._hasher.verify(password, user.password_hash):
            raise UnauthorizedError(_GENERIC_MESSAGE)

        self._users.record_login(user.user_id)
        token = self._tokens.issue(TokenPayload(user_id=user.user_id, email=user.email))
        return LoginResultDTO(access_token=token, user=to_auth_user_dto(user))
