"""Implementacion bcrypt del puerto PasswordHasher."""
import bcrypt

from app.application.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def verify(self, plain_password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    def hash(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
