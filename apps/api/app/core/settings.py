"""Configuracion de la aplicacion.

Toda la configuracion proviene de variables de entorno (ver .env.example).
No se permiten valores hardcoded en el resto del codigo.
"""
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Conexion a PostgreSQL armada desde host/usuario/password/nombre/puerto
    # (mismo patron que db/config/db_config.py: create_db_engine). La
    # contrasena se escapa con quote_plus para soportar caracteres especiales.
    db_host: str | None = Field(default=None, alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    db_user: str | None = Field(default=None, alias="DB_USER")
    db_password: str | None = Field(default=None, alias="DB_PASSWORD")
    db_name: str | None = Field(default=None, alias="DB_NAME")

    # Alternativa: URL completa. Si se define, tiene prioridad sobre DB_HOST/...
    database_url_override: str | None = Field(default=None, alias="DATABASE_URL")
    app_metadata_database_url: str | None = Field(default=None, alias="APP_METADATA_DATABASE_URL")

    api_env: str = Field(default="development", alias="API_ENV")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    auth_allowed_email_domain: str = Field(default="lazarza.com.mx", alias="AUTH_ALLOWED_EMAIL_DOMAIN")
    password_hash_algorithm: str = Field(default="bcrypt", alias="PASSWORD_HASH_ALGORITHM")
    auth_secret_key: str = Field(alias="AUTH_SECRET_KEY")
    auth_token_expire_minutes: int = Field(default=480, alias="AUTH_TOKEN_EXPIRE_MINUTES")

    etl_schema: str = Field(default="etl_execution_aws", alias="ETL_SCHEMA")

    cors_allowed_origins: str = Field(default="http://localhost:5173", alias="CORS_ALLOWED_ORIGINS")

    @model_validator(mode="after")
    def _require_connection_info(self) -> "Settings":
        has_parts = all([self.db_host, self.db_user, self.db_password, self.db_name])
        if not self.database_url_override and not has_parts:
            raise ValueError(
                "Define DATABASE_URL o el conjunto DB_HOST/DB_USER/DB_PASSWORD/DB_NAME"
            )
        return self

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        safe_password = quote_plus(self.db_password)  # type: ignore[arg-type]
        return f"postgresql://{self.db_user}:{safe_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def metadata_database_url(self) -> str:
        return self.app_metadata_database_url or self.database_url

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
