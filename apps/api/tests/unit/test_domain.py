"""Tests de la capa domain."""
from datetime import datetime, timezone

import pytest

from app.domain.services.execution_identity import (
    InvalidExecutionKeyError,
    build_execution_key,
    parse_execution_key,
)
from app.domain.value_objects.execution_status import ExecutionStatus
from app.domain.value_objects.institutional_email import (
    ForbiddenDomainError,
    InstitutionalEmail,
    InvalidEmailError,
)
from app.domain.value_objects.table_identifier import (
    InvalidTableIdentifierError,
    TableIdentifier,
)
from tests.conftest import make_execution

UTC = timezone.utc


class TestExecutionStatus:
    def test_parse_valid(self):
        assert ExecutionStatus.parse("SUCCESS") is ExecutionStatus.SUCCESS
        assert ExecutionStatus.parse("failed") is ExecutionStatus.FAILED
        assert ExecutionStatus.parse(" running ") is ExecutionStatus.RUNNING

    def test_parse_error_alias_maps_to_failed(self):
        # Varios ETL productores escriben status='error' en vez de 'FAILED'
        # (confirmado en produccion: etl_sad, etl_objetivo_rebanadas).
        assert ExecutionStatus.parse("error") is ExecutionStatus.FAILED
        assert ExecutionStatus.parse("ERROR") is ExecutionStatus.FAILED

    def test_parse_unknown_returns_none(self):
        assert ExecutionStatus.parse("BROKEN") is None
        assert ExecutionStatus.parse(None) is None

    def test_values(self):
        assert ExecutionStatus.values() == ["SUCCESS", "FAILED", "RUNNING", "WARNING", "CANCELLED"]

    def test_db_literals_includes_alias(self):
        assert ExecutionStatus.db_literals(ExecutionStatus.FAILED) == ["FAILED", "ERROR"]

    def test_db_literals_without_alias_returns_canonical_only(self):
        assert ExecutionStatus.db_literals(ExecutionStatus.SUCCESS) == ["SUCCESS"]


class TestInstitutionalEmail:
    def test_valid_email_normalized(self):
        email = InstitutionalEmail(value=" User@LAZARZA.com.mx ", allowed_domain="lazarza.com.mx")
        assert email.value == "user@lazarza.com.mx"

    def test_wrong_domain_rejected(self):
        with pytest.raises(ForbiddenDomainError):
            InstitutionalEmail(value="user@gmail.com", allowed_domain="lazarza.com.mx")

    def test_lookalike_domain_rejected(self):
        with pytest.raises(ForbiddenDomainError):
            InstitutionalEmail(value="user@fake-lazarza.com.mx.evil.com", allowed_domain="lazarza.com.mx")

    def test_invalid_format_rejected(self):
        with pytest.raises(InvalidEmailError):
            InstitutionalEmail(value="not-an-email", allowed_domain="lazarza.com.mx")


class TestTableIdentifier:
    def test_valid_identifier_quoted(self):
        table = TableIdentifier(schema_name="etl_execution_aws", table_name="etl_cobranza")
        assert table.qualified == '"etl_execution_aws"."etl_cobranza"'

    @pytest.mark.parametrize(
        "bad", ["etl; DROP TABLE x", "Etl_Upper", "1starts_with_digit", "", "name with spaces", 'quo"te']
    )
    def test_injection_attempts_rejected(self, bad):
        with pytest.raises(InvalidTableIdentifierError):
            TableIdentifier(schema_name="etl_execution_aws", table_name=bad)


class TestExecutionEntity:
    def test_effective_duration_prefers_recorded(self):
        assert make_execution(duration_seconds=120).effective_duration_seconds == 120

    def test_effective_duration_computed_from_times(self):
        execution = make_execution(
            duration_seconds=None,
            start_time=datetime(2026, 7, 1, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 7, 1, 10, 4, 30, tzinfo=UTC),
        )
        assert execution.effective_duration_seconds == 270

    def test_effective_duration_none_when_running(self):
        execution = make_execution(
            duration_seconds=None,
            end_time=None,
            status=ExecutionStatus.RUNNING,
            raw_status="RUNNING",
        )
        assert execution.effective_duration_seconds is None
        assert execution.is_running


class TestExecutionIdentity:
    def test_roundtrip_with_execution_id(self):
        execution = make_execution()
        key = parse_execution_key(build_execution_key(execution))
        assert key.etl_name == "etl_cobranza"
        assert key.key == "exec-1"
        assert key.start_time == execution.start_time

    def test_fallback_to_request_id(self):
        execution = make_execution(execution_id=None, request_id="req-9")
        assert parse_execution_key(build_execution_key(execution)).key == "req-9"

    def test_fallback_to_created_at(self):
        created = datetime(2026, 7, 1, 10, 5, tzinfo=UTC)
        execution = make_execution(execution_id=None, request_id=None, created_at=created)
        key = parse_execution_key(build_execution_key(execution))
        assert key.key == created.isoformat()
        assert key.start_time == execution.start_time

    @pytest.mark.parametrize("bad", ["", "solo-una-parte", "a::b", "etl::key::fecha-mala"])
    def test_invalid_keys_rejected(self, bad):
        with pytest.raises(InvalidExecutionKeyError):
            parse_execution_key(bad)
