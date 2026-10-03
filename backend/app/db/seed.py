"""
Database seeder for Development and Staging environments.
IMPORTANT: Clearly separates demo/mock data from production data (Principle 9).
"""
import sys
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import AdminLevel, UserRole
from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.user import Role, User
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate
from app.services.org_service import org_service
from app.services.user_service import user_service


def seed_development_data(db: Session, force: bool = False):
    if settings.APP_ENV == "production" and not force:
        logger.error("Refusing to seed demo data into PRODUCTION environment without explicit force flag.")
        return

    logger.info("Verifying system roles and permissions...")
    user_service.init_system_roles_and_permissions(db)

    # 1. Organizations: Nepal Administrative Hierarchy (Federal -> Province -> District -> Municipality)
    org_neoc = org_service.get_by_code(db, "NEOC-FED")
    if not org_neoc:
        logger.info("Seeding Level 1: National Emergency Operation Centre (NEOC)...")
        org_neoc = org_service.create_organization(
            db=db,
            org_in=OrganizationCreate(
                name="National Emergency Operation Centre (NEOC)",
                code="NEOC-FED",
                admin_level=AdminLevel.FEDERAL.value,
                contact_email="neoc@moha.gov.np",
                contact_phone="+977-1-4200045",
                latitude=27.7000,
                longitude=85.3333,
            ),
        )

    org_peoc = org_service.get_by_code(db, "PEOC-BAGMATI")
    if not org_peoc:
        logger.info("Seeding Level 2: Bagmati Province Emergency Operations Center...")
        org_peoc = org_service.create_organization(
            db=db,
            org_in=OrganizationCreate(
                name="Bagmati Provincial Emergency Operations Center",
                code="PEOC-BAGMATI",
                admin_level=AdminLevel.PROVINCIAL.value,
                parent_id=org_neoc.id,
                province_id=3,
                contact_email="peoc.bagmati@resq.gov.np",
                contact_phone="+977-57-520123",
                latitude=27.4285,
                longitude=85.0308,
            ),
        )

    org_deoc = org_service.get_by_code(db, "DEOC-KTM")
    if not org_deoc:
        logger.info("Seeding Level 3: Kathmandu District Emergency Operations Center...")
        org_deoc = org_service.create_organization(
            db=db,
            org_in=OrganizationCreate(
                name="Kathmandu District Emergency Operations Center",
                code="DEOC-KTM",
                admin_level=AdminLevel.DISTRICT.value,
                parent_id=org_peoc.id,
                province_id=3,
                district_name="Kathmandu",
                contact_email="deoc.ktm@resq.gov.np",
                contact_phone="+977-1-4262800",
                latitude=27.7172,
                longitude=85.3240,
            ),
        )

    org_palika = org_service.get_by_code(db, "PALIKA-KMC")
    if not org_palika:
        logger.info("Seeding Level 4: Kathmandu Metropolitan City Disaster Management Unit...")
        org_palika = org_service.create_organization(
            db=db,
            org_in=OrganizationCreate(
                name="Kathmandu Metropolitan City Disaster Management Unit",
                code="PALIKA-KMC",
                admin_level=AdminLevel.MUNICIPALITY.value,
                parent_id=org_deoc.id,
                province_id=3,
                district_name="Kathmandu",
                municipality_name="Kathmandu Metropolitan City",
                contact_email="disaster@kathmandu.gov.np",
                contact_phone="+977-1-4231481",
                latitude=27.7052,
                longitude=85.3148,
            ),
        )

    # 2. Seed Standard Administrative & Operational Users
    users_to_seed = [
        {
            "email": "superadmin@resq.gov.np",
            "full_name": "National Disaster Controller",
            "password": "EmergencyAdminPass#2026",
            "roles": [UserRole.SUPER_ADMIN.value],
            "org_id": org_neoc.id,
            "phone": "+977-9800000001",
        },
        {
            "email": "coordinator.ktm@resq.gov.np",
            "full_name": "Kathmandu Emergency Coordinator",
            "password": "EmergencyCoord#2026",
            "roles": [UserRole.EMERGENCY_COORDINATOR.value],
            "org_id": org_deoc.id,
            "phone": "+977-9800000002",
        },
        {
            "email": "officer.kmc@resq.gov.np",
            "full_name": "KMC Incident Officer",
            "password": "IncidentOfficer#2026",
            "roles": [UserRole.INCIDENT_OFFICER.value],
            "org_id": org_palika.id,
            "phone": "+977-9800000003",
        },
        {
            "email": "responder.ward1@resq.gov.np",
            "full_name": "Ward 1 Quick Response Leader",
            "password": "FieldResponder#2026",
            "roles": [UserRole.FIELD_RESPONDER.value],
            "org_id": org_palika.id,
            "phone": "+977-9800000004",
        },
        {
            "email": "doctor.triage@resq.gov.np",
            "full_name": "Emergency Medical Officer",
            "password": "MedicalOfficer#2026",
            "roles": [UserRole.MEDICAL_OFFICER.value],
            "org_id": org_deoc.id,
            "phone": "+977-9800000005",
        },
    ]

    for udata in users_to_seed:
        existing = user_service.get_by_email(db, udata["email"])
        if not existing:
            logger.info(f"Seeding user: {udata['email']} ({udata['roles']})...")
            user_service.create_user(
                db=db,
                user_in=UserCreate(
                    email=udata["email"],
                    full_name=udata["full_name"],
                    password=udata["password"],
                    roles=udata["roles"],
                    organization_id=udata["org_id"],
                    phone=udata["phone"],
                ),
            )

    logger.info("Development seeding completed successfully.")


if __name__ == "__main__":
    force_run = "--force" in sys.argv
    db = SessionLocal()
    try:
        seed_development_data(db, force=force_run)
    finally:
        db.close()
