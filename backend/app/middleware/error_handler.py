"""
Centralized exception handling for RESQ AGENT.
Returns standard, consistent error response payloads conforming to:
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-safe error message",
    "request_id": "uuid-here"
  }
}
Prevents internal stack trace leakage.
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger


def get_request_id(request: Request) -> str:
    """Safely extracts correlation ID assigned by middleware."""
    return getattr(request.state, "correlation_id", "unknown")


def register_exception_handlers(app: FastAPI):
    """Attach centralized exception handlers to FastAPI application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = get_request_id(request)
        logger.warning(f"Request validation failed [request_id={request_id}]: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "request_id": request_id,
                    "details": [
                        {"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")}
                        for err in exc.errors()
                    ],
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = get_request_id(request)
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            429: "RATE_LIMITED",
            503: "SERVICE_UNAVAILABLE",
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")

        # If detail is already formatted dict
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            content = exc.detail
            if "request_id" not in content["error"]:
                content["error"]["request_id"] = request_id
            return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                    "request_id": request_id,
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = get_request_id(request)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                    "request_id": request_id,
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        request_id = get_request_id(request)
        logger.error(f"Unhandled system error [request_id={request_id}]: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred. Please contact the system administrator.",
                    "request_id": request_id,
                }
            },
        )
