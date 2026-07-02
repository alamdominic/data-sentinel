"""Caso de uso: resolver el usuario autenticado desde un token."""
from app.application.dto.auth_dto import AuthUserDTO, to_auth_user_dto
from app.application.ports.token_provider import TokenProvider
from app.core.errors import UnauthorizedError
from app.domain.repositories.user_repository import UserRepository


class GetCurrentUserUseCase:
    def __init__(self, users: UserRepository, tokens: TokenProvider):
        self._users = users
        self._tokens = tokens

    def execute(self, token: str) -> AuthUserDTO:
        payload = self._tokens.decode(token)
        if payload is None:
            raise UnauthorizedError("Sesion invalida o expirada")
        user = self._users.get_by_id(payload.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Usuario no autorizado")
        return to_auth_user_dto(user)
