"""Schemas de entrada de la API."""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LoginRequest(CamelRequest):
    email: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=1, max_length=200)


class RegisterEtlRequest(CamelRequest):
    etl_name: str = Field(min_length=1, max_length=120)
    table_name: str = Field(min_length=1, max_length=120)
    schema_name: str | None = Field(default=None, max_length=120)
    display_name: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=2000)
    environment: str | None = Field(default=None, max_length=50)
    server_name: str | None = Field(default=None, max_length=120)


class SetEtlActiveRequest(CamelRequest):
    is_active: bool
