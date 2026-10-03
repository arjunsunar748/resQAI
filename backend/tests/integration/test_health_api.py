"""
Integration tests for health, liveness, readiness, and error handling formatting.
"""
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "api_v1" in data


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "request_id" in data
    assert "service" in data


def test_health_live_endpoint(client: TestClient):
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ALIVE"
    assert "request_id" in data


def test_health_ready_endpoint(client: TestClient):
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert "dependencies" in data
    assert data["dependencies"]["database"] == "CONNECTED"
    assert "request_id" in data

    # Verify zero secret or connection string leakage
    response_text = response.text.lower()
    assert "password" not in response_text
    assert "postgresql://" not in response_text
    assert "redis://" not in response_text


def test_centralized_error_handling_not_found(client: TestClient):
    response = client.get("/non-existent-tactical-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_ERROR"
    assert "request_id" in data["error"]


def test_centralized_error_handling_validation(client: TestClient):
    # Post invalid payload to an endpoint expecting JSON schema
    response = client.post("/api/v1/auth/login", json={"email": "not-an-email"})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert "request_id" in data["error"]
    assert "details" in data["error"]
