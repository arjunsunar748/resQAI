"""
Health and readiness probes for Docker, Kubernetes, and monitoring agents.
"""
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.db.session import check_db_connection

router = APIRouter(tags=["Health & Status"])


@router.get("/health")
def liveness_check():
    """Liveness probe: verifies that the FastAPI process is responsive."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@router.get("/ready")
def readiness_check():
    """Readiness probe: validates connectivity to primary database infrastructure."""
    db_connected = check_db_connection()
    if not db_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not healthy",
        )
    return {
        "status": "ready",
        "database": "connected",
        "app": settings.APP_NAME,
    }
