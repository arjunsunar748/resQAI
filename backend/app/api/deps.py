"""
FastAPI dependency injection for authentication, RBAC authorization, and request context.
"""
from typing import Callable, List, Optional, Tuple
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import UserRole
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.user_service import user_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_client_info(request: Request) -> Tuple[Optional[str], Optional[str]]:
    """Extract client IP address and User-Agent header safely."""
    # Check X-Forwarded-For if behind a proxy
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else None

    user_agent = request.headers.get("User-Agent")
    return client_ip, user_agent


def get_token_payload(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> dict:
    """
    Validate JWT signature, expiration, and ensure it has not been revoked.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except Exception:
        raise credentials_exception

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type (access token required)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload.get("jti")
    if jti and auth_service.is_token_revoked(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been terminated. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieve current authenticated user record from database.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )

    user = user_service.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or removed",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


def require_roles(*allowed_roles: str) -> Callable:
    """
    Enforces that the authenticated user possesses at least one of the permitted roles.
    SUPER_ADMIN always bypasses this check.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = {r.name for r in current_user.roles}
        if UserRole.SUPER_ADMIN.value in user_role_names:
            return current_user

        if not any(role in user_role_names for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {list(allowed_roles)}",
            )
        return current_user

    return role_checker


def require_permissions(*required_permissions: str) -> Callable:
    """
    Enforces that the user has all specified granular permissions.
    SUPER_ADMIN always bypasses this check.
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = {r.name for r in current_user.roles}
        if UserRole.SUPER_ADMIN.value in user_role_names:
            return current_user

        user_perms = auth_service.get_user_permissions(current_user)
        missing = [p for p in required_permissions if p not in user_perms]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Missing permissions: {missing}",
            )
        return current_user

    return permission_checker
