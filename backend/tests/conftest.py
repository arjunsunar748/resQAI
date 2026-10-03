"""
Pytest fixtures and configuration for RESQ AGENT test suite.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.constants import AdminLevel, UserRole
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationCreate
from app.schemas.user import UserCreate
from app.services.auth_service import auth_service
from app.services.org_service import org_service
from app.services.user_service import user_service

# Use PostgreSQL test database or local test schema
TEST_DATABASE_URL = settings.DATABASE_URL

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure database schema is created and system roles/permissions are initialized."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    user_service.init_system_roles_and_permissions(db)
    db.close()
    yield


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Yields a database session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_organization(db: Session) -> Organization:
    """Fixture providing a test disaster authority organization."""
    code = "TEST-DEOC-01"
    existing = org_service.get_by_code(db, code)
    if existing:
        return existing
    return org_service.create_organization(
        db=db,
        org_in=OrganizationCreate(
            name="Test Emergency Center",
            code=code,
            admin_level=AdminLevel.DISTRICT.value,
            province_id=3,
            district_name="Kathmandu",
        ),
    )


@pytest.fixture
def superadmin_user(db: Session, test_organization: Organization) -> User:
    email = "test.superadmin@resq.gov.np"
    user = user_service.get_by_email(db, email)
    if not user:
        user = user_service.create_user(
            db=db,
            user_in=UserCreate(
                email=email,
                full_name="Test Super Admin",
                password="SecureAdminPass#123",
                roles=[UserRole.SUPER_ADMIN.value],
                organization_id=test_organization.id,
            ),
        )
    return user


@pytest.fixture
def superadmin_token(superadmin_user: User) -> str:
    tokens = auth_service.create_tokens_for_user(superadmin_user)
    return tokens.access_token


@pytest.fixture
def responder_user(db: Session, test_organization: Organization) -> User:
    email = "test.responder@resq.gov.np"
    user = user_service.get_by_email(db, email)
    if not user:
        user = user_service.create_user(
            db=db,
            user_in=UserCreate(
                email=email,
                full_name="Test Field Responder",
                password="ResponderPass#123",
                roles=[UserRole.FIELD_RESPONDER.value],
                organization_id=test_organization.id,
            ),
        )
    return user


@pytest.fixture
def responder_token(responder_user: User) -> str:
    tokens = auth_service.create_tokens_for_user(responder_user)
    return tokens.access_token
