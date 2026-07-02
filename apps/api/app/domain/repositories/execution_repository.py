"""Contrato de acceso a ejecuciones ETL (solo lectura)."""
from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.execution import Execution
from app.domain.entities.registered_etl import RegisteredEtl
from app.domain.repositories.queries import (
    EtlAggregate,
    ExecutionFilters,
    PageSpec,
    SortSpec,
    TrendPoint,
)


class ExecutionRepository(ABC):
    """Todas las consultas son SELECT parametrizados sobre tablas registradas."""

    @abstractmethod
    def list_executions(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
        sort: SortSpec,
        page: PageSpec,
    ) -> tuple[list[Execution], int]:
        """Retorna (items, total) combinando las tablas registradas."""

    @abstractmethod
    def find_execution(
        self,
        etl: RegisteredEtl,
        key: str,
        start_time: datetime,
    ) -> Execution | None:
        """Busca una ejecucion por su clave compuesta."""

    @abstractmethod
    def aggregate(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> list[EtlAggregate]:
        """Agregados por ETL (conteos por estado, duraciones, ultima ejecucion)."""

    @abstractmethod
    def last_execution(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> Execution | None:
        """Ejecucion mas reciente entre las tablas dadas."""

    @abstractmethod
    def last_error(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> Execution | None:
        """Ejecucion fallida mas reciente entre las tablas dadas."""

    @abstractmethod
    def daily_trend(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> list[TrendPoint]:
        """Serie diaria de ejecuciones y fallos dentro del rango."""

    @abstractmethod
    def weekly_trend(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> list[TrendPoint]:
        """Serie semanal de ejecuciones y fallos dentro del rango."""

    @abstractmethod
    def monthly_trend(
        self,
        etls: list[RegisteredEtl],
        filters: ExecutionFilters,
    ) -> list[TrendPoint]:
        """Serie mensual de ejecuciones y fallos dentro del rango."""
