"""
RESQ AGENT - AI-Powered Disaster Response & Coordination Platform
Main FastAPI Application Entrypoint.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestCorrelationMiddleware, SecurityHeadersMiddleware
from app.db.session import SessionLocal, check_db_connection
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

# 1. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request Correlation & Tracing Middleware
app.add_middleware(RequestCorrelationMiddleware)

# 3. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-Process-Time"],
)


# Global Exception Handler: Sanitize uncaught errors to prevent sensitive internal leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    logger.error(f"Unhandled system error [Correlation ID: {correlation_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred. Please contact the system administrator.",
            "correlation_id": correlation_id,
        },
    )


# Root endpoints
@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "status": "operational",
        "version": "1.0.0",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health")
def root_health():
    return {"status": "online", "app": settings.APP_NAME}


# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
