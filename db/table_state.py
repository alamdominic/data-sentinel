"""Database table state inspection helpers."""

import logging
from sqlalchemy import text
from app.db.config.db_config import create_db_engine

logger = logging.getLogger(__name__)


def get_last_transfer_id(table_name: str, id_column: str):
    """Obtiene el último valor no nulo del id_column en la tabla.

    Returns:
        (value, status) donde status es: "ok", "empty", "not_found", "error"
    """
    try:
        engine = create_db_engine()
        if engine is None:
            logger.error("No se pudo crear el engine de PostgreSQL.")
            return None, "error"

        with engine.connect() as conn:
            check_query = text("SELECT to_regclass(:table)")
            table_exists = conn.execute(check_query, {"table": table_name}).scalar()

            if not table_exists:
                logger.error("La tabla '%s' no existe en la base de datos.", table_name)
                return None, "not_found"

            query = text(f"""
                SELECT "{id_column}"
                FROM {table_name}
                WHERE "{id_column}" IS NOT NULL
                ORDER BY "{id_column}" DESC NULLS LAST
                LIMIT 1
            """)
            result = conn.execute(query).scalar()

            if result is not None:
                logger.info("Último '%s' en '%s': %s", id_column, table_name, result)
                return result, "ok"
            else:
                logger.info("Tabla '%s' existe pero está vacía.", table_name)
                return None, "empty"

    except Exception as e:
        logger.error("Error obteniendo último '%s' de '%s': %s", id_column, table_name, e)
        return None, "error"
