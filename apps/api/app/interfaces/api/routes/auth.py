"""Rutas de autenticacion."""
from fastapi import APIRouter, Depends

from app.application.dto.auth_dto import AuthUserDTO, LoginResultDTO
from app.interfaces.api.dependencies import Container, get_container, get_current_user
from app.interfaces.api.schemas.requests import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResultDTO, response_model_by_alias=True)
def login(body: LoginRequest, container: Container = Depends(get_container)) -> LoginResultDTO:
    """Valida correo institucional y password hasheado. Retorna token de sesion."""
    return container.login_use_case.execute(body.email, body.password)


@router.get("/me", response_model=AuthUserDTO, response_model_by_alias=True)
def me(current_user: AuthUserDTO = Depends(get_current_user)) -> AuthUserDTO:
    """Usuario autenticado actual."""
    return current_user
