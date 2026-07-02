"""Tests del registro dinamico de ETLs (RF-013, RF-014)."""
import pytest

from app.application.use_cases.list_registered_etls_use_case import ListRegisteredEtlsUseCase
from app.application.use_cases.register_etl_table_use_case import RegisterEtlTableUseCase
from app.application.use_cases.set_etl_active_use_case import SetEtlActiveUseCase
from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from tests.conftest import FakeEtlRegistryRepository, make_etl

SCHEMA = "etl_execution_aws"


class TestRegisterEtlTableUseCase:
    def build(self, registry):
        return RegisterEtlTableUseCase(registry, SCHEMA)

    def test_registers_new_table(self, registry_repo):
        registry_repo.existing_tables.add((SCHEMA, "etl_facturacion"))
        dto = self.build(registry_repo).execute(
            etl_name="etl_facturacion",
            table_name="etl_facturacion",
            display_name="Facturacion",
            environment="prod",
            created_by=1,
        )
        assert dto.etl_name == "etl_facturacion"
        assert dto.is_active is True
        assert registry_repo.get_by_name("etl_facturacion") is not None

    def test_duplicate_name_conflict(self, registry_repo):
        registry_repo.existing_tables.add((SCHEMA, "etl_cobranza"))
        with pytest.raises(ConflictError):
            self.build(registry_repo).execute(etl_name="etl_cobranza", table_name="etl_cobranza")

    def test_duplicate_table_conflict(self, registry_repo):
        registry_repo.existing_tables.add((SCHEMA, "etl_cobranza"))
        with pytest.raises(ConflictError):
            self.build(registry_repo).execute(etl_name="otro_nombre", table_name="etl_cobranza")

    def test_missing_physical_table_rejected(self, registry_repo):
        with pytest.raises(ValidationAppError):
            self.build(registry_repo).execute(etl_name="etl_nueva", table_name="etl_nueva")

    def test_foreign_schema_rejected(self, registry_repo):
        with pytest.raises(ValidationAppError):
            self.build(registry_repo).execute(
                etl_name="etl_x", table_name="etl_x", schema_name="public"
            )


class TestListRegisteredEtlsUseCase:
    def test_active_only_by_default(self):
        registry = FakeEtlRegistryRepository(
            etls=[make_etl(), make_etl(etl_id=2, etl_name="etl_off", table_name="etl_off", is_active=False)]
        )
        result = ListRegisteredEtlsUseCase(registry).execute()
        assert [dto.etl_name for dto in result] == ["etl_cobranza"]

    def test_include_inactive(self):
        registry = FakeEtlRegistryRepository(
            etls=[make_etl(), make_etl(etl_id=2, etl_name="etl_off", table_name="etl_off", is_active=False)]
        )
        result = ListRegisteredEtlsUseCase(registry).execute(include_inactive=True)
        assert len(result) == 2


class TestSetEtlActiveUseCase:
    def test_deactivates(self, registry_repo):
        dto = SetEtlActiveUseCase(registry_repo).execute(1, False)
        assert dto.is_active is False

    def test_unknown_id_not_found(self, registry_repo):
        with pytest.raises(NotFoundError):
            SetEtlActiveUseCase(registry_repo).execute(999, True)
