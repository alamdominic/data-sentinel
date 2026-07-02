"""Fetches table schema metadata from PostgreSQL information_schema."""

import logging
from contextlib import closing
from app.db.config.db_config import create_db_engine

logger = logging.getLogger(__name__)


def get_table_schema_details(table_name: str) -> dict:
    """Obtiene metadatos detallados de columnas para una tabla específica.

    Args:
        table_name: Nombre completo de la tabla, e.g. '"schema"."table"'.

    Returns:
        dict col_name → {data_type, is_nullable, char_max_length, ...}
        Vacío si la tabla no existe o hay error.
    """
    schema, table = table_name.replace('"', "").split(".")
    query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            datetime_precision
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s;
    """
    schema_details = {}
    try:
        engine = create_db_engine()
        if engine is None:
            logger.error("Database configuration is missing or invalid.")
            return {}

        with closing(engine.raw_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(query, (schema, table))
                columns = cursor.fetchall()
                if not columns:
                    logger.warning("No se encontraron columnas para '%s'.", table_name)
                    return {}

                for (
                    col_name, data_type, is_nullable,
                    char_max_length, numeric_precision,
                    numeric_scale, datetime_precision,
                ) in columns:
                    schema_details[col_name] = {
                        "data_type": data_type,
                        "is_nullable": is_nullable,
                        "char_max_length": char_max_length,
                        "numeric_precision": numeric_precision,
                        "numeric_scale": numeric_scale,
                        "datetime_precision": datetime_precision,
                    }

                logger.info("Esquema obtenido para '%s': %d columnas.", table_name, len(schema_details))

    except Exception as e:
        logger.error("Error obteniendo esquema de '%s': %s", table_name, e)
        return {}

    return schema_details
