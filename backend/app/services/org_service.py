"""
Organization management service supporting Nepal administrative hierarchy.
"""
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.constants import AdminLevel, AuditAction
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.services.audit_service import audit_service


class OrganizationService:
    @staticmethod
    def get_by_id(db: Session, org_id: int) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.id == org_id, Organization.is_deleted == False).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.code == code.upper(), Organization.is_deleted == False).first()

    @classmethod
    def create_organization(
        cls,
        db: Session,
        org_in: OrganizationCreate,
        actor: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Organization:
        existing = cls.get_by_code(db, org_in.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization with code '{org_in.code}' already exists.",
            )

        if org_in.parent_id:
            parent = cls.get_by_id(db, org_in.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent organization ID {org_in.parent_id} does not exist.",
                )

        # Validate AdminLevel
        if org_in.admin_level not in [level.value for level in AdminLevel]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid admin_level. Must be one of: {[l.value for l in AdminLevel]}",
            )

        org = Organization(
            name=org_in.name,
            code=org_in.code.upper(),
            admin_level=org_in.admin_level,
            parent_id=org_in.parent_id,
            province_id=org_in.province_id,
            district_name=org_in.district_name,
            municipality_name=org_in.municipality_name,
            ward_number=org_in.ward_number,
            contact_email=org_in.contact_email,
            contact_phone=org_in.contact_phone,
            latitude=org_in.latitude,
            longitude=org_in.longitude,
            boundary_geojson=org_in.boundary_geojson,
            is_active=True,
        )
        db.add(org)
        db.commit()
        db.refresh(org)

        audit_service.create_audit_log(
            db=db,
            action=AuditAction.ORG_CREATE,
            entity_type="Organization",
            actor_id=actor.id if actor else None,
            organization_id=org.id,
            entity_id=str(org.id),
            ip_address=ip_address,
            user_agent=user_agent,
            changes={"name": org.name, "code": org.code, "admin_level": org.admin_level},
        )
        return org

    @classmethod
    def update_organization(
        cls,
        db: Session,
        org_id: int,
        org_in: OrganizationUpdate,
        actor: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Organization:
        org = cls.get_by_id(db, org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        changes = {}
        for field, value in org_in.model_dump(exclude_unset=True).items():
            current_val = getattr(org, field)
            if current_val != value:
                changes[field] = {"old": current_val, "new": value}
                setattr(org, field, value)

        db.commit()
        db.refresh(org)

        if changes:
            audit_service.create_audit_log(
                db=db,
                action=AuditAction.ORG_UPDATE,
                entity_type="Organization",
                actor_id=actor.id,
                organization_id=org.id,
                entity_id=str(org.id),
                ip_address=ip_address,
                user_agent=user_agent,
                changes=changes,
            )
        return org

    @staticmethod
    def list_organizations(
        db: Session,
        admin_level: Optional[str] = None,
        province_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Organization], int]:
        query = db.query(Organization).filter(Organization.is_deleted == False)
        if admin_level:
            query = query.filter(Organization.admin_level == admin_level)
        if province_id:
            query = query.filter(Organization.province_id == province_id)
        if parent_id:
            query = query.filter(Organization.parent_id == parent_id)

        total = query.count()
        orgs = (
            query.order_by(desc(Organization.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return orgs, total


org_service = OrganizationService()
