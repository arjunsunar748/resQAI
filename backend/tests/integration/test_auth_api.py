"""
Integration tests for authentication, login, refresh rotation, and logout.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def test_login_success(client: TestClient, superadmin_user: User):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": superadmin_user.email, "password": "SecureAdminPass#123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


def test_login_invalid_password(client: TestClient, superadmin_user: User):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": superadmin_user.email, "password": "IncorrectPassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert "Incorrect email or password" in data["error"]["message"]


def test_refresh_token_rotation(client: TestClient, superadmin_user: User):
    # Step 1: Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": superadmin_user.email, "password": "SecureAdminPass#123"},
    )
    refresh_token = login_res.json()["refresh_token"]

    # Step 2: Refresh token
    refresh_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    assert new_data["refresh_token"] != refresh_token  # Must be rotated

    # Step 3: Replay of used refresh token must be rejected
    replay_res = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert replay_res.status_code == 401
    data = replay_res.json()
    assert "error" in data
    assert "revoked" in data["error"]["message"].lower()


def test_logout_and_revocation(client: TestClient, superadmin_user: User):
    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": superadmin_user.email, "password": "SecureAdminPass#123"},
    )
    access_token = login_res.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # Verify access to /auth/me works
    me_res = client.get("/api/v1/auth/me", headers=auth_header)
    assert me_res.status_code == 200

    # Logout
    logout_res = client.post("/api/v1/auth/logout", headers=auth_header)
    assert logout_res.status_code == 200

    # Subsequent access with same token must now be rejected
    me_after_res = client.get("/api/v1/auth/me", headers=auth_header)
    assert me_after_res.status_code == 401
    data = me_after_res.json()
    assert "error" in data
    assert "terminated" in data["error"]["message"].lower()


def test_get_me_profile(client: TestClient, superadmin_token: str, superadmin_user: User):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == superadmin_user.email
    assert "permissions" in data
    assert len(data["permissions"]) > 0
    assert any(role["name"] == "SUPER_ADMIN" for role in data["roles"])
