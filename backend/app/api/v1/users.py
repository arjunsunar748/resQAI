"""
User management and role assignment endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_client_info, get_db, require_permissions
from app.core.constants import Permission
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserOut, UserRoleAssignRequest, UserUpdate
from app.services.auth_service import auth_service
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.USER_CREATE.value)),
):
    """Create a new user account with specified roles."""
    ip, ua = get_client_info(request)
    created = user_service.create_user(
        db=db,
        user_in=user_in,
        actor=current_user,
        ip_address=ip,
        user_agent=ua,
    )
    user_out = UserOut.model_validate(created)
    user_out.permissions = list(auth_service.get_user_permissions(created))
    return user_out


@router.get("/", response_model=PaginatedResponse[UserOut])
def list_users(
    organization_id: Optional[int] = Query(None, description="Filter users by organization"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.USER_READ.value)),
):
    """List registered users with pagination."""
    items, total = user_service.list_users(
        db=db,
        organization_id=organization_id,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    results = []
    for user in items:
        out = UserOut.model_validate(user)
        out.permissions = list(auth_service.get_user_permissions(user))
        results.append(out)

    return PaginatedResponse(
        items=results,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.USER_READ.value)),
):
    """Retrieve user details by ID."""
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    out = UserOut.model_validate(user)
    out.permissions = list(auth_service.get_user_permissions(user))
    return out


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.USER_UPDATE.value)),
):
    """Update user information."""
    ip, ua = get_client_info(request)
    updated = user_service.update_user(
        db=db,
        user_id=user_id,
        user_in=user_in,
        actor=current_user,
        ip_address=ip,
        user_agent=ua,
    )
    out = UserOut.model_validate(updated)
    out.permissions = list(auth_service.get_user_permissions(updated))
    return out


@router.post("/{user_id}/roles", response_model=UserOut)
def assign_user_roles(
    user_id: int,
    role_in: UserRoleAssignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.USER_ASSIGN_ROLE.value)),
):
    """Assign or modify operational roles for a user (audited)."""
    ip, ua = get_client_info(request)
    updated = user_service.assign_roles(
        db=db,
        user_id=user_id,
        role_names=role_in.role_names,
        actor=current_user,
        ip_address=ip,
        user_agent=ua,
    )
    out = UserOut.model_validate(updated)
    out.permissions = list(auth_service.get_user_permissions(updated))
    return out
