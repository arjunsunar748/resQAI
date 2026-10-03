"""
Cryptographic security module: Bcrypt password hashing, JWT token lifecycle,
and HMAC tamper-evident checksums for audit trails.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from typing import Any, Dict, List, Optional, Tuple
import uuid
import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt with salt.
    Truncates to 72 bytes if necessary to prevent bcrypt overflow.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against an existing bcrypt hash.
    Safely handles edge cases and avoids timing attacks.
    """
    try:
        plain_bytes = plain_password.encode("utf-8")
        if len(plain_bytes) > 72:
            plain_bytes = plain_bytes[:72]
        return bcrypt.checkpw(plain_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: str,
    roles: List[str],
    permissions: List[str],
    org_id: Optional[int] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a signed JWT access token containing subject identity,
    organization context, assigned roles, and resolved permissions.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
        "roles": roles,
        "permissions": permissions,
        "org_id": org_id,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> Tuple[str, str]:
    """
    Generate a signed JWT refresh token with unique jti (JWT ID).
    Returns (token_string, jti).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    jti = str(uuid.uuid4())
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
        "jti": jti,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and cryptographically verify a JWT token.
    Raises JWTError on expired, tampered, or invalid tokens.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def compute_audit_checksum(
    actor_id: Optional[str],
    action: str,
    entity_type: str,
    entity_id: Optional[str],
    timestamp_iso: str,
    details_str: str,
) -> str:
    """
    Generate an HMAC-SHA256 cryptographic signature for an audit log entry.
    Ensures that any direct database manipulation or tampering is detected.
    """
    message = f"{actor_id}:{action}:{entity_type}:{entity_id}:{timestamp_iso}:{details_str}".encode("utf-8")
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), message, hashlib.sha256).hexdigest()
