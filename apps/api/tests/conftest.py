"""Fakes compartidos para tests unitarios de logica de negocio."""
from datetime import datetime, timezone

import pytest

from app.application.ports.password_hasher import PasswordHasher
from app.application.ports.token_provider import TokenPayload, TokenProvider
from app.domain.entities.execution import Execution
from app.domain.entities.registered_etl import RegisteredEtl
from app.domain.entities.user import User
from app.domain.repositories.etl_registry_repository import (
    EtlRegistryRepository,
    NewEtlRegistration,
)
from app.domain.repositories.execution_repository import ExecutionRepository
from app.domain.repositories.queries import (
    EtlAggregate,
    ExecutionFilters,
    PageSpec,
    SortSpec,
    TrendPoint,
)
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.execution_status import ExecutionStatus

UTC = timezone.utc


def make_execution(**overrides) -> Execution:
    defaults = dict(
        etl_name="etl_cobranza",
        execution_id="exec-1",
        start_time=datetime(2026, 7, 1, 10, 0, tzinfo=UTC),
        end_time=datetime(2026, 7, 1, 10, 5, tzinfo=UTC),
        duration_seconds=300,
        status=ExecutionStatus.SUCCESS,
        raw_status="SUCCESS",
        created_at=datetime(2026, 7, 1, 10, 5, tzinfo=UTC),
    )
    defaults.update(overrides)
    return Execution(**defaults)


def make_etl(**overrides) -> RegisteredEtl:
    defaults = dict(
        etl_id=1,
        etl_name="etl_cobranza",
        schema_name="etl_execution_aws",
        table_name="etl_cobranza",
        display_name="Cobranza",
        environment="prod",
        server_name="aws-01",
        is_active=True,
    )
    defaults.update(overrides)
    return RegisteredEtl(**defaults)


def make_user(**overrides) -> User:
    defaults = dict(
        user_id=1,
        email="becario.bi@lazarza.com.mx",
        password_hash="$2b$fakehash",
        role="admin",
        full_name="Becario BI",
        is_active=True,
    )
    defaults.update(overrides)
    return User(**defaults)


class FakeExecutionRepository(ExecutionRepository):
    def __init__(self):
        self.executions: list[Execution] = []
        self.aggregates: list[EtlAggregate] = []
        self.trend: list[TrendPoint] = []
        self.last_filters: ExecutionFilters | None = None
        self.last_sort: SortSpec | None = None
        self.last_page: PageSpec | None = None

    def list_executions(self, etls, filters, sort, page):
        self.last_filters, self.last_sort, self.last_page = filters, sort, page
        start = page.offset
        return self.executions[start : start + page.limit], len(self.executions)

    def find_execution(self, etl, key, start_time):
        for execution in self.executions:
            if execution.etl_name == etl.etl_name and execution.start_time == start_time and (
                execution.execution_id == key or execution.request_id == key
            ):
                return execution
        return None

    def aggregate(self, etls, filters):
        self.last_filters = filters
        return self.aggregates

    def last_execution(self, etls, filters):
        return self.executions[0] if self.executions else None

    def last_error(self, etls, filters):
        failed = [e for e in self.executions if e.status is ExecutionStatus.FAILED]
        return failed[0] if failed else None

    def daily_trend(self, etls, filters):
        return self.trend

    def weekly_trend(self, etls, filters):
        return self.trend

    def monthly_trend(self, etls, filters):
        return self.trend


class FakeEtlRegistryRepository(EtlRegistryRepository):
    def __init__(self, etls: list[RegisteredEtl] | None = None, existing_tables=None):
        self.etls = etls or []
        self.existing_tables = set(existing_tables or [])
        self._next_id = max((etl.etl_id for etl in self.etls), default=0) + 1

    def list_etls(self, active_only=True, environment=None, server_name=None):
        result = [etl for etl in self.etls if not active_only or etl.is_active]
        if environment:
            result = [etl for etl in result if etl.environment == environment]
        if server_name:
            result = [etl for etl in result if etl.server_name == server_name]
        return sorted(result, key=lambda etl: etl.etl_name)

    def get_by_name(self, etl_name):
        return next((etl for etl in self.etls if etl.etl_name == etl_name), None)

    def get_by_table(self, schema_name, table_name):
        return next(
            (
                etl
                for etl in self.etls
                if etl.schema_name == schema_name and etl.table_name == table_name
            ),
            None,
        )

    def table_exists(self, schema_name, table_name):
        return (schema_name, table_name) in self.existing_tables

    def register(self, registration: NewEtlRegistration):
        etl = RegisteredEtl(
            etl_id=self._next_id,
            etl_name=registration.etl_name,
            schema_name=registration.schema_name,
            table_name=registration.table_name,
            display_name=registration.display_name,
            description=registration.description,
            environment=registration.environment,
            server_name=registration.server_name,
            is_active=True,
        )
        self._next_id += 1
        self.etls.append(etl)
        return etl

    def set_active(self, etl_id, is_active):
        for index, etl in enumerate(self.etls):
            if etl.etl_id == etl_id:
                updated = RegisteredEtl(
                    etl_id=etl.etl_id,
                    etl_name=etl.etl_name,
                    schema_name=etl.schema_name,
                    table_name=etl.table_name,
                    display_name=etl.display_name,
                    description=etl.description,
                    environment=etl.environment,
                    server_name=etl.server_name,
                    is_active=is_active,
                )
                self.etls[index] = updated
                return updated
        return None


class FakeUserRepository(UserRepository):
    def __init__(self, users: list[User] | None = None):
        self.users = users or []
        self.logins: list[int] = []

    def get_active_by_email(self, email):
        return next(
            (u for u in self.users if u.email.lower() == email.lower() and u.is_active), None
        )

    def get_by_id(self, user_id):
        return next((u for u in self.users if u.user_id == user_id), None)

    def record_login(self, user_id):
        self.logins.append(user_id)


class FakePasswordHasher(PasswordHasher):
    def verify(self, plain_password, password_hash):
        return password_hash == f"hash::{plain_password}"

    def hash(self, plain_password):
        return f"hash::{plain_password}"


class FakeTokenProvider(TokenProvider):
    def issue(self, payload: TokenPayload) -> str:
        return f"token::{payload.user_id}::{payload.email}"

    def decode(self, token: str) -> TokenPayload | None:
        if not token.startswith("token::"):
            return None
        _, user_id, email = token.split("::", 2)
        return TokenPayload(user_id=int(user_id), email=email)


@pytest.fixture
def execution_repo():
    return FakeExecutionRepository()


@pytest.fixture
def registry_repo():
    return FakeEtlRegistryRepository(etls=[make_etl()])


@pytest.fixture
def user_repo():
    return FakeUserRepository(users=[make_user(password_hash="hash::secret")])
