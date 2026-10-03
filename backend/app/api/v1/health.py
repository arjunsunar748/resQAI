"""
Health and readiness probes for container orchestrators, uptime checks, and load balancers.
Ensures zero sensitive credentials or connection strings are ever leaked in output.
"""
from typing import Dict
from fastapi import APIRouter, HTTPException, Request, status
import redis

from app.core.config import settings
from app.db.session import check_db_connection

router = APIRouter(tags=["System Health & Diagnostics"])


def check_redis_connection() -> bool:
    """Probes the Redis cache/queue service safely without exposing credentials."""
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=1.5, socket_connect_timeout=1.5)
        return r.ping()
    except Exception:
        return False


@router.get("/health")
def health_check(request: Request):
    """
    Standard health check endpoint.
    Returns overall system operational status.
    """
    request_id = getattr(request.state, "correlation_id", "unknown")
    return {
        "status": "UP",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "request_id": request_id,
    }


@router.get("/health/live")
def liveness_check(request: Request):
    """
    Liveness probe: verifies that the FastAPI event loop is running and accepting connections.
    """
    request_id = getattr(request.state, "correlation_id", "unknown")
    return {
        "status": "ALIVE",
        "service": settings.APP_NAME,
        "request_id": request_id,
    }


@router.get("/health/ready")
def readiness_check(request: Request):
    """
    Readiness probe: validates required runtime dependencies (Database).
    Never exposes internal connection strings, credentials, or host topologies.
    """
    request_id = getattr(request.state, "correlation_id", "unknown")
    db_ok = check_db_connection()
    redis_ok = check_redis_connection()

    dependencies: Dict[str, str] = {
        "database": "CONNECTED" if db_ok else "DISCONNECTED",
        "redis": "CONNECTED" if redis_ok else "DISCONNECTED",
    }

    # In production/staging, database is strictly required for readiness
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Primary storage dependency is not ready",
                    "request_id": request_id,
                }
            },
        )

    return {
        "status": "READY",
        "service": settings.APP_NAME,
        "dependencies": dependencies,
        "request_id": request_id,
    }
