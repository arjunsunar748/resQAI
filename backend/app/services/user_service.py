"""
User and RBAC role lifecycle management service.
"""
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.constants import AuditAction, Permission as PermEnum, UserRole as RoleEnum, ROLE_PERMISSIONS_MAP
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import Permission, Role, User
from app.schemas.user import UserCreate, UserUpdate
from app.services.audit_service import audit_service
from app.core.logging import logger


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower(), User.is_deleted == False).first()

    @classmethod
    def create_user(
        cls,
        db: Session,
        user_in: UserCreate,
        actor: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        """Create a new user with hashed password, assigned roles, and audit trail."""
        existing_email = cls.get_by_email(db, user_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address is already registered.",
            )

        if user_in.phone:
            existing_phone = db.query(User).filter(User.phone == user_in.phone, User.is_deleted == False).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this phone number is already registered.",
                )

        if user_in.organization_id:
            org = db.query(Organization).filter(Organization.id == user_in.organization_id, Organization.is_deleted == False).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target organization not found.",
                )

        hashed = hash_password(user_in.password)
        new_user = User(
            email=user_in.email.lower(),
            phone=user_in.phone,
            full_name=user_in.full_name,
            hashed_password=hashed,
            organization_id=user_in.organization_id,
            preferred_locale=user_in.preferred_locale,
            is_active=True,
            is_verified=True if actor else False,
        )

        # Resolve roles
        assigned_roles = []
        if user_in.roles:
            for role_name in user_in.roles:
                role = db.query(Role).filter(Role.name == role_name).first()
                if role:
                    assigned_roles.append(role)
        else:
            default_role = db.query(Role).filter(Role.name == RoleEnum.FIELD_RESPONDER.value).first()
            if default_role:
                assigned_roles.append(default_role)

        new_user.roles = assigned_roles
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        audit_service.create_audit_log(
            db=db,
            action=AuditAction.USER_CREATE,
            entity_type="User",
            actor_id=actor.id if actor else new_user.id,
            organization_id=new_user.organization_id,
            entity_id=str(new_user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            changes={"email": new_user.email, "roles": [r.name for r in assigned_roles]},
        )
        return new_user

    @classmethod
    def update_user(
        cls,
        db: Session,
        user_id: int,
        user_in: UserUpdate,
        actor: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        user = cls.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        changes = {}
        if user_in.full_name is not None and user_in.full_name != user.full_name:
            changes["full_name"] = {"old": user.full_name, "new": user_in.full_name}
            user.full_name = user_in.full_name
        if user_in.phone is not None and user_in.phone != user.phone:
            changes["phone"] = {"old": user.phone, "new": user_in.phone}
            user.phone = user_in.phone
        if user_in.preferred_locale is not None and user_in.preferred_locale != user.preferred_locale:
            changes["preferred_locale"] = {"old": user.preferred_locale, "new": user_in.preferred_locale}
            user.preferred_locale = user_in.preferred_locale
        if user_in.organization_id is not None and user_in.organization_id != user.organization_id:
            changes["organization_id"] = {"old": user.organization_id, "new": user_in.organization_id}
            user.organization_id = user_in.organization_id
        if user_in.is_active is not None and user_in.is_active != user.is_active:
            changes["is_active"] = {"old": user.is_active, "new": user_in.is_active}
            user.is_active = user_in.is_active
        if user_in.is_verified is not None and user_in.is_verified != user.is_verified:
            changes["is_verified"] = {"old": user.is_verified, "new": user_in.is_verified}
            user.is_verified = user_in.is_verified

        db.commit()
        db.refresh(user)

        if changes:
            audit_service.create_audit_log(
                db=db,
                action=AuditAction.USER_UPDATE,
                entity_type="User",
                actor_id=actor.id,
                organization_id=user.organization_id,
                entity_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                changes=changes,
            )
        return user

    @classmethod
    def assign_roles(
        cls,
        db: Session,
        user_id: int,
        role_names: List[str],
        actor: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> User:
        user = cls.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        matched_roles = db.query(Role).filter(Role.name.in_(role_names)).all()
        if len(matched_roles) != len(role_names):
            found_names = {r.name for r in matched_roles}
            missing = set(role_names) - found_names
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The following roles do not exist: {', '.join(missing)}",
            )

        old_roles = [r.name for r in user.roles]
        user.roles = matched_roles
        db.commit()
        db.refresh(user)

        audit_service.create_audit_log(
            db=db,
            action=AuditAction.USER_ROLE_ASSIGN,
            entity_type="User",
            actor_id=actor.id,
            organization_id=user.organization_id,
            entity_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            changes={"old_roles": old_roles, "new_roles": [r.name for r in matched_roles]},
        )
        return user

    @staticmethod
    def list_users(
        db: Session,
        organization_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[User], int]:
        query = db.query(User).filter(User.is_deleted == False)
        if organization_id:
            query = query.filter(User.organization_id == organization_id)
        total = query.count()
        users = (
            query.order_by(desc(User.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return users, total

    @staticmethod
    def init_system_roles_and_permissions(db: Session):
        """
        Idempotent database initializer: seeds standard roles and permissions.
        """
        # 1. Seed Permissions
        existing_perms = {p.code: p for p in db.query(Permission).all()}
        for perm in PermEnum:
            if perm.value not in existing_perms:
                new_perm = Permission(code=perm.value, description=f"Permission {perm.value}")
                db.add(new_perm)
        db.commit()

        # Re-fetch all permissions
        all_perms = {p.code: p for p in db.query(Permission).all()}

        # 2. Seed Roles and map permissions
        for role_enum, perm_set in ROLE_PERMISSIONS_MAP.items():
            role = db.query(Role).filter(Role.name == role_enum.value).first()
            if not role:
                role = Role(
                    name=role_enum.value,
                    description=f"System role: {role_enum.value}",
                    is_system_role=True,
                )
                db.add(role)
                db.commit()
                db.refresh(role)

            # Sync permissions
            target_permissions = [all_perms[p.value] for p in perm_set if p.value in all_perms]
            role.permissions = target_permissions
            db.commit()

        logger.info("System roles and permissions verified/initialized.")


user_service = UserService()
