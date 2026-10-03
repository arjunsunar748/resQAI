"""
RESQ AGENT - AI-Powered Disaster Response & Coordination Platform
Main FastAPI Application Entrypoint.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.api.v1.health import router as health_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestCorrelationMiddleware, SecurityHeadersMiddleware
from app.db.session import SessionLocal, check_db_connection
from app.middleware.error_handler import register_exception_handlers
from app.services.user_service import user_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    setup_logging()
    logger.info(f"Initializing {settings.APP_NAME} [Env: {settings.APP_ENV}]...")
    
    # Verify DB connectivity
    if check_db_connection():
        logger.info("Database connectivity established successfully.")
        # Ensure system roles and permissions are seeded
        db = SessionLocal()
        try:
            user_service.init_system_roles_and_permissions(db)
        except Exception as exc:
            logger.error(f"Failed to seed system roles/permissions: {exc}")
        finally:
            db.close()
    else:
        logger.warning("Database connection could not be established on startup.")

    yield
    # --- Shutdown ---
    logger.info(f"Shutting down {settings.APP_NAME} gracefully...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "Production-grade, government-ready disaster response coordination platform "
        "providing multi-level incident triage, GIS mapping, resource mobilization, "
        "and human-in-the-loop AI decision support."
    ),
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG or settings.APP_ENV != "production" else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG or settings.APP_ENV != "production" else None,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG or settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

# 1. Centralized Exception Handlers (Standard Error Envelope)
register_exception_handlers(app)

# 2. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 3. Request Correlation & Tracing Middleware
app.add_middleware(RequestCorrelationMiddleware)

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time"],
)

# Root service discovery
@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "status": "operational",
        "version": "1.0.0",
        "api_v1": settings.API_V1_STR,
    }

# Mount health routes directly at root (/health, /health/live, /health/ready)
app.include_router(health_router)

# Mount API v1 router (/api/v1/...)
app.include_router(api_router, prefix=settings.API_V1_STR)
