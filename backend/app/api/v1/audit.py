"""
Audit log query and cryptographic integrity verification endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permissions
from app.core.constants import Permission
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogOut
from app.schemas.common import PaginatedResponse
from app.services.audit_service import audit_service

router = APIRouter(prefix="/audit-logs", tags=["Audit & Compliance"])


@router.get("/", response_model=PaginatedResponse[AuditLogOut])
def list_audit_logs(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    actor_id: Optional[int] = Query(None, description="Filter by acting officer/user"),
    action: Optional[str] = Query(None, description="Filter by specific audit action"),
    entity_type: Optional[str] = Query(None, description="Filter by target entity type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.AUDIT_LOG_READ.value)),
):
    """
    Query system activity audit trail with pagination and filters.
    Requires AUDIT_LOG_READ permission.
    """
    items, total = audit_service.get_logs(
        db=db,
        organization_id=organization_id,
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse(
        items=[AuditLogOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{log_id}/verify")
def verify_audit_log_integrity(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(Permission.AUDIT_LOG_READ.value)),
):
    """
    Cryptographically verify the HMAC-SHA256 signature of an audit log entry.
    Returns whether the record remains unaltered.
    """
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log entry not found")

    is_valid = audit_service.verify_integrity(log)
    return {
        "log_id": log.id,
        "is_tamper_free": is_valid,
        "recorded_at": log.created_at,
        "action": log.action,
        "checksum": log.checksum,
    }
