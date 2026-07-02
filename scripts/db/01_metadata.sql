-- DATA SENTINEL - Tablas de metadatos
-- Ejecutar con un usuario administrador de la base.
-- Base: 02-DATABASE_CONTRACT.md

-- Usuarios autorizados de la plataforma
CREATE TABLE IF NOT EXISTS etl_execution_aws.app_users (
    user_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(150),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_app_users_email ON etl_execution_aws.app_users (email);

CREATE INDEX IF NOT EXISTS idx_app_users_is_active ON etl_execution_aws.app_users (is_active);

-- Registro dinamico de tablas ETL
CREATE TABLE IF NOT EXISTS etl_execution_aws.etl_registry (
    etl_id BIGSERIAL PRIMARY KEY,
    etl_name VARCHAR(120) NOT NULL UNIQUE,
    schema_name VARCHAR(120) NOT NULL DEFAULT 'etl_execution_aws',
    table_name VARCHAR(120) NOT NULL,
    display_name VARCHAR(150),
    description TEXT,
    environment VARCHAR(50),
    server_name VARCHAR(120),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT REFERENCES etl_execution_aws.app_users (user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_etl_registry_table UNIQUE (schema_name, table_name),
    CONSTRAINT chk_etl_registry_schema CHECK (
        schema_name = 'etl_execution_aws'
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_etl_registry_name ON etl_execution_aws.etl_registry (etl_name);

CREATE INDEX IF NOT EXISTS idx_etl_registry_active ON etl_execution_aws.etl_registry (is_active);

CREATE INDEX IF NOT EXISTS idx_etl_registry_environment ON etl_execution_aws.etl_registry (environment);

-- Permisos recomendados (reemplazar <readonly_user> y <metadata_user>):
-- GRANT USAGE ON SCHEMA etl_execution_aws TO <readonly_user>;
-- GRANT SELECT ON ALL TABLES IN SCHEMA etl_execution_aws TO <readonly_user>;
-- GRANT SELECT, UPDATE (last_login_at, updated_at) ON etl_execution_aws.app_users TO <metadata_user>;
-- GRANT SELECT, INSERT, UPDATE ON etl_execution_aws.etl_registry TO <metadata_user>;
-- GRANT USAGE ON SEQUENCE etl_execution_aws.etl_registry_etl_id_seq TO <metadata_user>;