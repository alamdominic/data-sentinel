"""Tests de validadores centralizados."""
import pytest

from app.application.validators.etl_registration_validator import validate_registration
from app.application.validators.filter_validator import validate_execution_filters
from app.application.validators.pagination_validator import validate_pagination
from app.application.validators.sort_validator import validate_sort
from app.core.errors import ValidationAppError
from app.domain.value_objects.execution_status import ExecutionStatus


class TestFilterValidator:
    def test_defaults_are_none(self):
        filters = validate_execution_filters()
        assert filters.start_date is None
        assert filters.status is None

    def test_parses_dates_and_status(self):
        filters = validate_execution_filters(
            start_date="2026-07-01", end_date="2026-07-02T23:59:59", status="failed"
        )
        assert filters.start_date is not None and filters.start_date.tzinfo is not None
        assert filters.status is ExecutionStatus.FAILED

    def test_invalid_date_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_execution_filters(start_date="ayer")

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_execution_filters(status="EXPLODED")

    def test_inverted_range_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_execution_filters(start_date="2026-07-02", end_date="2026-07-01")

    def test_long_text_filter_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_execution_filters(source_file="x" * 201)

    def test_blank_text_normalized_to_none(self):
        assert validate_execution_filters(request_id="   ").request_id is None


class TestPaginationValidator:
    def test_defaults(self):
        page = validate_pagination()
        assert page.page == 1
        assert page.limit == 25
        assert page.offset == 0

    def test_offset_computation(self):
        assert validate_pagination(page=3, limit=20).offset == 40

    @pytest.mark.parametrize("page,limit", [(0, 25), (1, 0), (1, 101), (-1, -5)])
    def test_out_of_range_rejected(self, page, limit):
        with pytest.raises(ValidationAppError):
            validate_pagination(page=page, limit=limit)


class TestSortValidator:
    def test_default_sort(self):
        sort = validate_sort()
        assert sort.column == "start_time"
        assert sort.direction == "desc"

    def test_maps_camel_case_whitelist(self):
        sort = validate_sort("durationSeconds", "asc")
        assert sort.column == "duration_seconds"
        assert sort.direction == "asc"

    def test_unknown_column_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_sort("password_hash")

    def test_sql_injection_in_direction_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_sort("startTime", "desc; DROP TABLE x")


class TestEtlRegistrationValidator:
    ALLOWED = "etl_execution_aws"

    def test_valid_registration_normalized(self):
        registration = validate_registration(
            etl_name=" etl_facturacion ",
            table_name=" ETL_FACTURACION ",
            allowed_schema=self.ALLOWED,
            display_name=" Facturacion ",
        )
        assert registration.etl_name == "etl_facturacion"
        assert registration.table_name == "etl_facturacion"
        assert registration.schema_name == self.ALLOWED
        assert registration.display_name == "Facturacion"

    def test_wrong_schema_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_registration(
                etl_name="x", table_name="tabla", allowed_schema=self.ALLOWED, schema_name="public"
            )

    def test_invalid_table_name_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_registration(
                etl_name="x", table_name="tabla; DROP", allowed_schema=self.ALLOWED
            )

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationAppError):
            validate_registration(etl_name="  ", table_name="tabla", allowed_schema=self.ALLOWED)
