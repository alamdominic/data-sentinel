"""Rutas de administracion del registro dinamico de ETLs."""
from fastapi import APIRouter, Depends, Query

from app.application.dto.auth_dto import AuthUserDTO
from app.application.dto.etl_registry_dto import EtlRegistryDTO
from app.interfaces.api.dependencies import Container, get_container, get_current_user
from app.interfaces.api.schemas.requests import RegisterEtlRequest, SetEtlActiveRequest

router = APIRouter(prefix="/api/etl-registry", tags=["etl-registry"])


@router.get("", response_model=list[EtlRegistryDTO], response_model_by_alias=True)
def list_registered_etls(
    include_inactive: bool = Query(default=False, alias="includeInactive"),
    container: Container = Depends(get_container),
    _user: AuthUserDTO = Depends(get_current_user),
) -> list[EtlRegistryDTO]:
    return container.list_registered_etls_use_case.execute(include_inactive=include_inactive)


@router.post("", response_model=EtlRegistryDTO, response_model_by_alias=True, status_code=201)
def register_etl(
    body: RegisterEtlRequest,
    container: Container = Depends(get_container),
    current_user: AuthUserDTO = Depends(get_current_user),
) -> EtlRegistryDTO:
    """Registra una tabla ETL nueva. Valida schema y existencia fisica de la tabla."""
    return container.register_etl_table_use_case.execute(
        etl_name=body.etl_name,
        table_name=body.table_name,
        schema_name=body.schema_name,
        display_name=body.display_name,
        description=body.description,
        environment=body.environment,
        server_name=body.server_name,
        created_by=current_user.user_id,
    )


@router.patch("/{etl_id}", response_model=EtlRegistryDTO, response_model_by_alias=True)
def set_etl_active(
    etl_id: int,
    body: SetEtlActiveRequest,
    container: Container = Depends(get_container),
    _user: AuthUserDTO = Depends(get_current_user),
) -> EtlRegistryDTO:
    """Activa o desactiva un ETL registrado."""
    return container.set_etl_active_use_case.execute(etl_id, body.is_active)
