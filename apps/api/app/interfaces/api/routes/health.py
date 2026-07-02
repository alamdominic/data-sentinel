"""GET /api/health - estado de la aplicacion y conectividad a base."""
from fastapi import APIRouter, Depends

from app.interfaces.api.dependencies import Container, get_container

router = APIRouter(tags=["health"])


@router.get("/api/health")
def health(container: Container = Depends(get_container)) -> dict:
    database = "up"
    try:
        with container.pools.metadata_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
    except Exception:
        database = "down"
    return {
        "status": "ok" if database == "up" else "degraded",
        "environment": container.settings.api_env,
        "database": database,
    }
