"""
Token revocation / blacklist model for secure logout and token rotation.
"""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.db.base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(64), unique=True, index=True, nullable=False)
    token_type = Column(String(20), nullable=False)  # "access" or "refresh"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(255), nullable=True)
