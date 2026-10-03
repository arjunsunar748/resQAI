"""
Integration tests for Audit trail queries and HMAC cryptographic verification.
"""
from fastapi.testclient import TestClient


def test_audit_logs_unauthorized(client: TestClient, responder_token: str):
    # Field responder does not have AUDIT_LOG_READ permission
    response = client.get(
        "/api/v1/audit-logs/",
        headers={"Authorization": f"Bearer {responder_token}"},
    )
    assert response.status_code == 403


def test_audit_logs_authorized_query_and_verification(
    client: TestClient,
    superadmin_token: str,
):
    # Query audit logs
    response = client.get(
        "/api/v1/audit-logs/",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0

    first_log_id = data["items"][0]["id"]

    # Verify HMAC integrity via verification endpoint
    verify_res = client.get(
        f"/api/v1/audit-logs/{first_log_id}/verify",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["log_id"] == first_log_id
    assert verify_data["is_tamper_free"] is True
    assert "checksum" in verify_data
