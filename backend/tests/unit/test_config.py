"""
Unit tests for configuration validation and settings security constraints.
"""
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_jwt_secret_length_validation():
    # Secret key shorter than 32 characters must be rejected
    with pytest.raises(ValidationError):
        Settings(JWT_SECRET="short-insecure-key")


def test_cors_origins_parsing():
    settings_obj = Settings(
        JWT_SECRET="a" * 32,
        CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
    )
    assert len(settings_obj.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in settings_obj.CORS_ORIGINS


def test_nepal_localization_defaults():
    settings_obj = Settings(JWT_SECRET="a" * 32)
    assert settings_obj.DEFAULT_COUNTRY_CODE == "NPL"
    assert "ne" in settings_obj.SUPPORTED_LOCALES
    assert "en" in settings_obj.SUPPORTED_LOCALES
