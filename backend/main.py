"""
ResQ Agent - Backend Entrypoint Forwarder.
Imports the configured enterprise FastAPI application from app.main.
"""
from app.main import app

__all__ = ["app"]