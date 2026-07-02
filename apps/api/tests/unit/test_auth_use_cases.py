"""Tests de casos de uso de autenticacion."""
import pytest

from app.application.use_cases.get_current_user_use_case import GetCurrentUserUseCase
from app.application.use_cases.login_use_case import LoginUseCase
from app.core.errors import UnauthorizedError
from tests.conftest import FakePasswordHasher, FakeTokenProvider, FakeUserRepository, make_user

DOMAIN = "lazarza.com.mx"


def build_login(users: FakeUserRepository) -> LoginUseCase:
    return LoginUseCase(users, FakePasswordHasher(), FakeTokenProvider(), DOMAIN)


class TestLoginUseCase:
    def test_successful_login(self, user_repo):
        result = build_login(user_repo).execute("becario.bi@lazarza.com.mx", "secret")
        assert result.access_token.startswith("token::")
        assert result.user.email == "becario.bi@lazarza.com.mx"
        assert user_repo.logins == [1]

    def test_login_never_returns_password_hash(self, user_repo):
        result = build_login(user_repo).execute("becario.bi@lazarza.com.mx", "secret")
        assert "passwordHash" not in result.model_dump(by_alias=True)["user"]

    def test_foreign_domain_rejected(self, user_repo):
        with pytest.raises(UnauthorizedError, match="dominio institucional"):
            build_login(user_repo).execute("becario.bi@gmail.com", "secret")
        assert user_repo.logins == []

    def test_wrong_password_rejected_generic(self, user_repo):
        with pytest.raises(UnauthorizedError, match="Credenciales invalidas"):
            build_login(user_repo).execute("becario.bi@lazarza.com.mx", "wrong")

    def test_unknown_user_rejected_generic(self, user_repo):
        with pytest.raises(UnauthorizedError, match="Credenciales invalidas"):
            build_login(user_repo).execute("otro@lazarza.com.mx", "secret")

    def test_inactive_user_rejected(self):
        users = FakeUserRepository(
            users=[make_user(is_active=False, password_hash="hash::secret")]
        )
        with pytest.raises(UnauthorizedError):
            build_login(users).execute("becario.bi@lazarza.com.mx", "secret")

    def test_empty_password_rejected(self, user_repo):
        with pytest.raises(UnauthorizedError):
            build_login(user_repo).execute("becario.bi@lazarza.com.mx", "")


class TestGetCurrentUserUseCase:
    def test_valid_token_returns_user(self, user_repo):
        use_case = GetCurrentUserUseCase(user_repo, FakeTokenProvider())
        user = use_case.execute("token::1::becario.bi@lazarza.com.mx")
        assert user.user_id == 1

    def test_invalid_token_rejected(self, user_repo):
        use_case = GetCurrentUserUseCase(user_repo, FakeTokenProvider())
        with pytest.raises(UnauthorizedError):
            use_case.execute("garbage")

    def test_deleted_user_rejected(self):
        use_case = GetCurrentUserUseCase(FakeUserRepository(), FakeTokenProvider())
        with pytest.raises(UnauthorizedError):
            use_case.execute("token::99::ghost@lazarza.com.mx")
