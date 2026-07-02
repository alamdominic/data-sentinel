"""Mapeo uniforme de errores a respuestas HTTP.

Nunca se exponen queries, stack traces ni detalles internos.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.logging import get_logger

logger = get_logger("datasentinel.errors")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        if exc.http_status >= 500:
            logger.exception("Error interno en %s: %s", request.url.path, exc.message)
        return JSONResponse(status_code=exc.http_status, content=exc.to_payload())

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {"field": ".".join(str(part) for part in error.get("loc", [])), "issue": error.get("msg")}
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Parametros invalidos",
                    "details": details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error no controlado en %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "Error interno", "details": []}
            },
        )
