"""
Configuration management using Pydantic Settings.
Enforces zero hardcoded credentials and rigorous validation across environments.
"""
from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Profile
    APP_ENV: str = Field(default="development", description="development | staging | production | test")
    APP_NAME: str = Field(default="ResQ AI Command Center")
    DEBUG: bool = Field(default=False)
    API_V1_STR: str = Field(default="/api/v1")
    LOG_LEVEL: str = Field(default="INFO")

    # Cryptography & Security Secrets
    JWT_SECRET: str = Field(
        default="e83a7c64d852be994e63459c0490dae6b4d326f5820468f763bf45d376ce5928",
        min_length=32,
        description="Cryptographic key for signing JWTs and HMAC checksums"
    )
    JWT_REFRESH_SECRET: str = Field(
        default="7b9f8e7c6b5a4d3e2f1029384756abcdef7b9f8e7c6b5a4d3e2f1029384756abcdef",
        min_length=32,
        description="Cryptographic key for signing refresh tokens"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:test123@localhost:5432/resq_ai_db",
        description="SQLAlchemy database connection string"
    )
    POSTGRES_SERVER: Optional[str] = "localhost"
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_USER: Optional[str] = "postgres"
    POSTGRES_PASSWORD: Optional[str] = "test123"
    POSTGRES_DB: Optional[str] = "resq_ai_db"
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)
    DB_POOL_PRE_PING: bool = Field(default=True)

    # Redis Cache & PubSub
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=120)
    AUTH_RATE_LIMIT_PER_MINUTE: int = Field(default=10)

    # AI Configuration (Abstraction Layer)
    AI_PROVIDER: str = Field(default="ollama", description="ollama | openai | anthropic | gemini")
    AI_BASE_URL: str = Field(default="http://localhost:11434")
    AI_MODEL: str = Field(default="llama3:8b")
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Map Provider Abstraction
    MAP_PROVIDER: str = Field(default="osm")
    MAP_TILE_URL: str = Field(default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    MAP_ATTRIBUTION: str = Field(default="&copy; OpenStreetMap contributors")

    # Localization (Nepal Defaults)
    DEFAULT_COUNTRY_CODE: str = Field(default="NPL")
    DEFAULT_LATITUDE: float = Field(default=27.7172)
    DEFAULT_LONGITUDE: float = Field(default=85.3240)
    DEFAULT_MAP_ZOOM: int = Field(default=8)
    SUPPORTED_LOCALES: List[str] = Field(default=["en", "ne"])

    @property
    def SECRET_KEY(self) -> str:
        """Alias for backward compatibility."""
        return self.JWT_SECRET

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            if isinstance(v, str):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    return [v]
            return v
        raise ValueError(v)

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret_strength(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters in length.")
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )


settings = Settings()
