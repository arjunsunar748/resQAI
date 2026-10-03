"""
Authentication, token rotation, and session management service.
"""
from datetime import datetime, timezone
from typing import Optional, Set
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import AuditAction
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.token_blacklist import RevokedToken
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.services.audit_service import audit_service


class AuthService:
    @staticmethod
    def get_user_permissions(user: User) -> Set[str]:
        """Aggregate all distinct permission codes across all assigned roles."""
        perms = set()
        for role in user.roles:
            for perm in role.permissions:
                perms.add(perm.code)
        return perms

    @classmethod
    def create_tokens_for_user(cls, user: User) -> TokenResponse:
        roles = [r.name for r in user.roles]
        permissions = list(cls.get_user_permissions(user))
        
        access_token = create_access_token(
            subject=str(user.id),
            roles=roles,
            permissions=permissions,
            org_id=user.organization_id,
        )
        refresh_token, _ = create_refresh_token(subject=str(user.id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    @classmethod
    def authenticate_user(
        cls,
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """
        Verify credentials, update last login, and log audit trail.
        """
        user = db.query(User).filter(User.email == email.lower(), User.is_deleted == False).first()
        
        if not user or not verify_password(password, user.hashed_password):
            audit_service.create_audit_log(
                db=db,
                action=AuditAction.AUTH_LOGIN_FAILED,
                entity_type="User",
                actor_id=user.id if user else None,
                entity_id=str(user.id) if user else email,
                ip_address=ip_address,
                user_agent=user_agent,
                changes={"reason": "Invalid credentials", "attempted_email": email},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been deactivated. Contact your Emergency Operation Administrator.",
            )

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()

        audit_service.create_audit_log(
            db=db,
            action=AuditAction.AUTH_LOGIN_SUCCESS,
            entity_type="User",
            actor_id=user.id,
            organization_id=user.organization_id,
            entity_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return user

    @classmethod
    def refresh_tokens(
        cls,
        db: Session,
        refresh_token_str: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenResponse:
        """
        Exchange a valid refresh token for a new access token and rotate the refresh token.
        Revokes the previous refresh token to prevent replay attacks.
        """
        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for refresh",
            )

        jti = payload.get("jti")
        # Check blacklist
        is_revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account inactive or not found",
            )

        # Revoke the used refresh token (Token Rotation)
        exp_timestamp = payload.get("exp", 0)
        revoked_token = RevokedToken(
            jti=jti,
            token_type="refresh",
            user_id=user.id,
            expires_at=datetime.fromtimestamp(exp_timestamp, tz=timezone.utc),
            revoked_at=datetime.now(timezone.utc),
            reason="Token refreshed (Rotation)",
        )
        db.add(revoked_token)
        db.commit()

        audit_service.create_audit_log(
            db=db,
            action=AuditAction.AUTH_TOKEN_REFRESH,
            entity_type="User",
            actor_id=user.id,
            organization_id=user.organization_id,
            entity_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return cls.create_tokens_for_user(user)

    @classmethod
    def revoke_token(
        cls,
        db: Session,
        token_payload: dict,
        reason: str = "User logout",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Blacklist an access or refresh token by its JTI.
        """
        jti = token_payload.get("jti")
        if not jti:
            return

        # Check if already blacklisted
        existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
        if existing:
            return

        exp_timestamp = token_payload.get("exp", 0)
        user_id = int(token_payload.get("sub")) if token_payload.get("sub") else None

        revoked = RevokedToken(
            jti=jti,
            token_type=token_payload.get("type", "access"),
            user_id=user_id,
            expires_at=datetime.fromtimestamp(exp_timestamp, tz=timezone.utc),
            revoked_at=datetime.now(timezone.utc),
            reason=reason,
        )
        db.add(revoked)
        db.commit()

        if user_id:
            audit_service.create_audit_log(
                db=db,
                action=AuditAction.AUTH_LOGOUT,
                entity_type="User",
                actor_id=user_id,
                entity_id=str(user_id),
                ip_address=ip_address,
                user_agent=user_agent,
                changes={"reason": reason},
            )

    @staticmethod
    def is_token_revoked(db: Session, jti: str) -> bool:
        """Check if a token's JTI is in the revocation blacklist."""
        return db.query(RevokedToken).filter(RevokedToken.jti == jti).first() is not None


auth_service = AuthService()
