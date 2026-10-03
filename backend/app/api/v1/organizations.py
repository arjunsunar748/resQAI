"""
Organization management endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_client_info, get_db, require_permissions
from app.core.constants import Permission
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.organization import OrganizationCreate, OrganizationOut, OrganizationUpdate
from app.services.org_service import org_service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("/", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_in: OrganizationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.ORG_CREATE.value)),
):
    """Register a new administrative or operational organization."""
    ip, ua = get_client_info(request)
    return org_service.create_organization(
        db=db,
        org_in=org_in,
        actor=current_user,
        ip_address=ip,
        user_agent=ua,
    )


@router.get("/", response_model=PaginatedResponse[OrganizationOut])
def list_organizations(
    admin_level: Optional[str] = Query(None, description="Filter by administrative level"),
    province_id: Optional[int] = Query(None, ge=1, le=7, description="Filter by Province ID (1-7)"),
    parent_id: Optional[int] = Query(None, description="Filter by parent organization ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.ORG_READ.value)),
):
    """List organizations with administrative level and provincial filters."""
    items, total = org_service.list_organizations(
        db=db,
        admin_level=admin_level,
        province_id=province_id,
        parent_id=parent_id,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        items=[OrganizationOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.ORG_READ.value)),
):
    """Retrieve organization details by ID."""
    org = org_service.get_by_id(db, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return OrganizationOut.model_validate(org)


@router.put("/{org_id}", response_model=OrganizationOut)
def update_organization(
    org_id: int,
    org_in: OrganizationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.ORG_UPDATE.value)),
):
    """Update organization details (requires ORG_UPDATE permission)."""
    ip, ua = get_client_info(request)
    return org_service.update_organization(
        db=db,
        org_id=org_id,
        org_in=org_in,
        actor=current_user,
        ip_address=ip,
        user_agent=ua,
    )
