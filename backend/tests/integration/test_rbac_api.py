"""
Integration tests for Role-Based Access Control (RBAC) and permission boundaries.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.constants import AdminLevel, UserRole
from app.models.user import User


def test_unauthenticated_request_rejected(client: TestClient):
    response = client.get("/api/v1/organizations/")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data


def test_permission_enforcement_forbidden(client: TestClient, responder_token: str):
    # Field responder does NOT have ORG_CREATE permission
    payload = {
        "name": "Unauthorized Org",
        "code": "UNAUTH-01",
        "admin_level": AdminLevel.DISTRICT.value,
    }
    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers={"Authorization": f"Bearer {responder_token}"},
    )
    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert "Insufficient privileges" in data["error"]["message"]


def test_superadmin_full_access(client: TestClient, superadmin_token: str):
    # Superadmin has full access to create organizations
    payload = {
        "name": "Superadmin Created Org",
        "code": "SAC-01",
        "admin_level": AdminLevel.MUNICIPALITY.value,
        "province_id": 3,
    }
    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 201
    assert response.json()["code"] == "SAC-01"


def test_user_role_assignment_and_privilege_escalation(
    client: TestClient,
    superadmin_token: str,
    responder_user: User,
    responder_token: str,
):
    # Field responder initially forbidden from creating users
    create_user_payload = {
        "email": "new.member@resq.gov.np",
        "full_name": "New Team Member",
        "password": "Password#123",
        "roles": [UserRole.FIELD_RESPONDER.value],
    }
    res_forbidden = client.post(
        "/api/v1/users/",
        json=create_user_payload,
        headers={"Authorization": f"Bearer {responder_token}"},
    )
    assert res_forbidden.status_code == 403
    assert "error" in res_forbidden.json()

    # Superadmin assigns ORG_ADMIN role to responder
    assign_res = client.post(
        f"/api/v1/users/{responder_user.id}/roles",
        json={"role_names": [UserRole.ORG_ADMIN.value]},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert assign_res.status_code == 200
    roles = [r["name"] for r in assign_res.json()["roles"]]
    assert UserRole.ORG_ADMIN.value in roles
