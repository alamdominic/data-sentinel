"""Implementacion JWT (HS256) del puerto TokenProvider."""
from datetime import datetime, timedelta, timezone

import jwt

from app.application.ports.token_provider import TokenPayload, TokenProvider

_ALGORITHM = "HS256"


class JwtTokenProvider(TokenProvider):
    def __init__(self, secret_key: str, expire_minutes: int):
        self._secret_key = secret_key
        self._expire_minutes = expire_minutes

    def issue(self, payload: TokenPayload) -> str:
        now = datetime.now(timezone.utc)
        claims = {
            "sub": str(payload.user_id),
            "email": payload.email,
            "iat": now,
            "exp": now + timedelta(minutes=self._expire_minutes),
        }
        return jwt.encode(claims, self._secret_key, algorithm=_ALGORITHM)

    def decode(self, token: str) -> TokenPayload | None:
        try:
            claims = jwt.decode(token, self._secret_key, algorithms=[_ALGORITHM])
            return TokenPayload(user_id=int(claims["sub"]), email=str(claims.get("email", "")))
        except (jwt.PyJWTError, KeyError, ValueError):
            return None
