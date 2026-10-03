"""
Authentication and token lifecycle endpoints.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_client_info, get_current_user, get_db, get_token_payload
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserOut
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    login_in: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Authenticate emergency responder or officer via credentials.
    Issues JWT access token and rotating refresh token.
    """
    ip, ua = get_client_info(request)
    user = auth_service.authenticate_user(
        db=db,
        email=login_in.email,
        password=login_in.password,
        ip_address=ip,
        user_agent=ua,
    )
    return auth_service.create_tokens_for_user(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_in: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Rotate refresh token and issue a fresh access token.
    """
    ip, ua = get_client_info(request)
    return auth_service.refresh_tokens(
        db=db,
        refresh_token_str=refresh_in.refresh_token,
        ip_address=ip,
        user_agent=ua,
    )


@router.post("/logout")
def logout(
    request: Request,
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db),
):
    """
    Revoke current active token, invalidating the session.
    """
    ip, ua = get_client_info(request)
    auth_service.revoke_token(
        db=db,
        token_payload=payload,
        reason="User explicit logout",
        ip_address=ip,
        user_agent=ua,
    )
    return {"success": True, "message": "Successfully logged out and session revoked."}


@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve profile details, assigned roles, and operational permissions of the caller.
    """
    permissions = list(auth_service.get_user_permissions(current_user))
    user_out = UserOut.model_validate(current_user)
    user_out.permissions = permissions
    return user_out
