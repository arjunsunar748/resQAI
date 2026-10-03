"""
Integration tests for Organization hierarchy and administrative level validation.
"""
from fastapi.testclient import TestClient

from app.core.constants import AdminLevel


def test_create_organization_valid(client: TestClient, superadmin_token: str):
    payload = {
        "name": "Gandaki Provincial EOC",
        "code": "PEOC-GANDAKI",
        "admin_level": AdminLevel.PROVINCIAL.value,
        "province_id": 4,
        "contact_email": "peoc.gandaki@resq.gov.np",
        "contact_phone": "+977-61-520000",
        "latitude": 28.2096,
        "longitude": 83.9856,
    }
    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "PEOC-GANDAKI"
    assert data["admin_level"] == AdminLevel.PROVINCIAL.value
    assert data["province_id"] == 4


def test_create_organization_invalid_admin_level(client: TestClient, superadmin_token: str):
    payload = {
        "name": "Invalid Level Org",
        "code": "INVALID-01",
        "admin_level": "NON_EXISTENT_LEVEL",
    }
    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Invalid admin_level" in data["error"]["message"]


def test_duplicate_organization_code_rejected(client: TestClient, superadmin_token: str):
    payload = {
        "name": "Duplicate Code Org",
        "code": "DUP-CODE-01",
        "admin_level": AdminLevel.DISTRICT.value,
    }
    res1 = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert res1.status_code == 201

    res2 = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert res2.status_code == 400
    data = res2.json()
    assert "error" in data
    assert "already exists" in data["error"]["message"]


def test_list_and_filter_organizations(client: TestClient, superadmin_token: str):
    response = client.get(
        "/api/v1/organizations/",
        params={"admin_level": AdminLevel.DISTRICT.value, "page": 1, "page_size": 10},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    for item in data["items"]:
        assert item["admin_level"] == AdminLevel.DISTRICT.value
