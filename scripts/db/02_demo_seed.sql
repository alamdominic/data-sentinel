-- DATA SENTINEL - Datos demo para desarrollo local
-- Crea dos tablas ETL de ejemplo con ejecuciones y las registra.
-- NO ejecutar en produccion.

-- Tablas de ejecucion demo (DDL base de ddl_base.sql)
CREATE TABLE IF NOT EXISTS etl_execution_aws.etl_cobranza (
    execution_id VARCHAR(50),
    etl_version VARCHAR(50),
    execution_type VARCHAR(20),
    source_file TEXT,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    records_extracted INTEGER NOT NULL DEFAULT 0,
    records_loaded INTEGER NOT NULL DEFAULT 0,
    records_rejected INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL,
    error_message TEXT,
    error_stacktrace TEXT,
    request_id VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS etl_execution_aws.etl_clientes (
    LIKE etl_execution_aws.etl_cobranza INCLUDING ALL
);

CREATE INDEX IF NOT EXISTS idx_etl_cobranza_start_time
ON etl_execution_aws.etl_cobranza (start_time DESC);

CREATE INDEX IF NOT EXISTS idx_etl_clientes_start_time
ON etl_execution_aws.etl_clientes (start_time DESC);

-- Ejecuciones demo de los ultimos 14 dias
INSERT INTO etl_execution_aws.etl_cobranza
    (execution_id, etl_version, execution_type, source_file, start_time, end_time,
     duration_seconds, records_extracted, records_loaded, records_rejected, status,
     error_message, request_id)
SELECT
    'cob-' || day_offset,
    '1.4.' || (day_offset % 3),
    CASE WHEN day_offset % 5 = 0 THEN 'MANUAL' ELSE 'SCHEDULED' END,
    's3://lazarza-etl/cobranza/archivo_' || day_offset || '.csv',
    NOW() - (day_offset || ' days')::interval - interval '6 hours',
    NOW() - (day_offset || ' days')::interval - interval '6 hours'
        + ((180 + day_offset * 7) || ' seconds')::interval,
    180 + day_offset * 7,
    10000 + day_offset * 120,
    9950 + day_offset * 118,
    day_offset % 4,
    CASE WHEN day_offset % 7 = 3 THEN 'FAILED'
         WHEN day_offset % 11 = 5 THEN 'WARNING'
         ELSE 'SUCCESS' END,
    CASE WHEN day_offset % 7 = 3
         THEN 'Timeout al conectar con el origen de datos' END,
    'req-cob-' || day_offset
FROM generate_series(0, 13) AS day_offset;

INSERT INTO etl_execution_aws.etl_clientes
    (execution_id, etl_version, execution_type, source_file, start_time, end_time,
     duration_seconds, records_extracted, records_loaded, records_rejected, status,
     error_message, request_id)
SELECT
    'cli-' || day_offset,
    '2.0.1',
    'SCHEDULED',
    's3://lazarza-etl/clientes/clientes_' || day_offset || '.parquet',
    NOW() - (day_offset || ' days')::interval - interval '4 hours',
    CASE WHEN day_offset = 0 THEN NULL
         ELSE NOW() - (day_offset || ' days')::interval - interval '4 hours'
              + ((240 + day_offset * 5) || ' seconds')::interval END,
    CASE WHEN day_offset = 0 THEN NULL ELSE 240 + day_offset * 5 END,
    5000 + day_offset * 40,
    CASE WHEN day_offset = 0 THEN 0 ELSE 5000 + day_offset * 40 END,
    0,
    CASE WHEN day_offset = 0 THEN 'RUNNING'
         WHEN day_offset % 6 = 2 THEN 'FAILED'
         ELSE 'SUCCESS' END,
    CASE WHEN day_offset % 6 = 2 AND day_offset <> 0
         THEN 'Violacion de llave unica en staging' END,
    'req-cli-' || day_offset
FROM generate_series(0, 13) AS day_offset;

-- Registro dinamico inicial
INSERT INTO etl_execution_aws.etl_registry
    (etl_name, schema_name, table_name, display_name, description, environment, server_name)
VALUES
    ('etl_cobranza', 'etl_execution_aws', 'etl_cobranza', 'Cobranza',
     'Carga diaria de cobranza desde S3', 'prod', 'aws-etl-01'),
    ('etl_clientes', 'etl_execution_aws', 'etl_clientes', 'Clientes',
     'Sincronizacion de catalogo de clientes', 'prod', 'aws-etl-01')
ON CONFLICT (etl_name) DO NOTHING;
