"""
Database Base class and declarative mixins for RESQ AGENT.
"""
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        # Default table name is lowercase class name
        return cls.__name__.lower()


Base = declarative_base(cls=CustomBase)


class TimestampMixin:
    """Adds standardized UTC created_at and updated_at timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class SoftDeleteMixin:
    """Supports soft deletion for regulatory compliance and audit trails."""
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
