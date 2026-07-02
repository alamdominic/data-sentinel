"""Inyeccion de dependencias FastAPI.

Los repositorios, puertos y casos de uso se construyen una vez en el
startup (lifespan) y se exponen aqui via Depends.
"""
from dataclasses import dataclass

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.dto.auth_dto import AuthUserDTO
from app.application.use_cases.etl_scope import EtlScopeResolver
from app.application.use_cases.get_current_user_use_case import GetCurrentUserUseCase
from app.application.use_cases.get_dashboard_use_case import GetDashboardUseCase
from app.application.use_cases.get_execution_detail_use_case import GetExecutionDetailUseCase
from app.application.use_cases.get_statistics_use_case import GetStatisticsUseCase
from app.application.use_cases.list_executions_use_case import ListExecutionsUseCase
from app.application.use_cases.list_registered_etls_use_case import ListRegisteredEtlsUseCase
from app.application.use_cases.login_use_case import LoginUseCase
from app.application.use_cases.register_etl_table_use_case import RegisterEtlTableUseCase
from app.application.use_cases.set_etl_active_use_case import SetEtlActiveUseCase
from app.core.errors import UnauthorizedError
from app.core.settings import Settings, get_settings
from app.infrastructure.database.pools import DatabasePools
from app.infrastructure.repositories.postgres_etl_registry_repository import (
    PostgresEtlRegistryRepository,
)
from app.infrastructure.repositories.postgres_execution_repository import (
    PostgresExecutionRepository,
)
from app.infrastructure.repositories.postgres_user_repository import PostgresUserRepository
from app.infrastructure.security.bcrypt_hasher import BcryptPasswordHasher
from app.infrastructure.security.jwt_provider import JwtTokenProvider

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class Container:
    settings: Settings
    pools: DatabasePools
    login_use_case: LoginUseCase
    get_current_user_use_case: GetCurrentUserUseCase
    list_executions_use_case: ListExecutionsUseCase
    get_execution_detail_use_case: GetExecutionDetailUseCase
    get_dashboard_use_case: GetDashboardUseCase
    get_statistics_use_case: GetStatisticsUseCase
    list_registered_etls_use_case: ListRegisteredEtlsUseCase
    register_etl_table_use_case: RegisterEtlTableUseCase
    set_etl_active_use_case: SetEtlActiveUseCase


def build_container(settings: Settings | None = None) -> Container:
    settings = settings or get_settings()
    pools = DatabasePools(settings)

    executions = PostgresExecutionRepository(pools.etl_pool)
    registry = PostgresEtlRegistryRepository(pools.metadata_pool, settings.etl_schema)
    users = PostgresUserRepository(pools.metadata_pool, settings.etl_schema)
    hasher = BcryptPasswordHasher()
    tokens = JwtTokenProvider(settings.auth_secret_key, settings.auth_token_expire_minutes)
    scope = EtlScopeResolver(registry)

    return Container(
        settings=settings,
        pools=pools,
        login_use_case=LoginUseCase(users, hasher, tokens, settings.auth_allowed_email_domain),
        get_current_user_use_case=GetCurrentUserUseCase(users, tokens),
        list_executions_use_case=ListExecutionsUseCase(executions, scope),
        get_execution_detail_use_case=GetExecutionDetailUseCase(executions, registry),
        get_dashboard_use_case=GetDashboardUseCase(executions, scope),
        get_statistics_use_case=GetStatisticsUseCase(executions, scope),
        list_registered_etls_use_case=ListRegisteredEtlsUseCase(registry),
        register_etl_table_use_case=RegisterEtlTableUseCase(registry, settings.etl_schema),
        set_etl_active_use_case=SetEtlActiveUseCase(registry),
    )


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    container: Container = Depends(get_container),
) -> AuthUserDTO:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Se requiere autenticacion")
    return container.get_current_user_use_case.execute(credentials.credentials)
