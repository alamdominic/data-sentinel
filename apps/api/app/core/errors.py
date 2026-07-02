"""Errores de aplicacion con codigo uniforme.

Formato de respuesta HTTP:
{"error": {"code": "...", "message": "...", "details": []}}

Nunca se exponen queries, credenciales ni stack traces.
"""
from typing import Any


class AppError(Exception):
    code = "INTERNAL_ERROR"
    http_status = 500

    def __init__(self, message: str = "Error interno", details: list[Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []

    def to_payload(self) -> dict[str, Any]:
        return {"error": {"code": self.code, "message": self.message, "details": self.details}}


class ValidationAppError(AppError):
    code = "VALIDATION_ERROR"
    http_status = 400

    def __init__(self, message: str = "Parametros invalidos", details: list[Any] | None = None):
        super().__init__(message, details)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    http_status = 404

    def __init__(self, message: str = "Recurso no encontrado", details: list[Any] | None = None):
        super().__init__(message, details)


class UnauthorizedError(AppError):
    code = "UNAUTHORIZED"
    http_status = 401

    def __init__(self, message: str = "Credenciales invalidas", details: list[Any] | None = None):
        super().__init__(message, details)


class ConflictError(AppError):
    code = "CONFLICT"
    http_status = 409

    def __init__(self, message: str = "Conflicto con el estado actual", details: list[Any] | None = None):
        super().__init__(message, details)


class DatabaseAppError(AppError):
    code = "DATABASE_ERROR"
    http_status = 500

    def __init__(self, message: str = "Error de base de datos", details: list[Any] | None = None):
        super().__init__(message, details)
