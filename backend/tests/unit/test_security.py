"""
Unit tests for cryptographic security: Bcrypt, JWT tokens, and HMAC checksums.
"""
from datetime import timedelta
import time
from jose import JWTError
import pytest

from app.core.security import (
    compute_audit_checksum,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    plain = "SuperRescue#Pass2026"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_password_truncation_safeguard():
    # Bcrypt standard limit is 72 bytes; ensure passwords longer than 72 bytes do not crash
    long_password = "A" * 120
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed) is True
    assert verify_password("A" * 71, hashed) is False


def test_access_token_creation_and_decoding():
    subject = "user-999"
    roles = ["EMERGENCY_COORDINATOR"]
    permissions = ["incident:verify", "resource:dispatch"]
    org_id = 42

    token = create_access_token(
        subject=subject,
        roles=roles,
        permissions=permissions,
        org_id=org_id,
        expires_delta=timedelta(minutes=15),
    )
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "access"
    assert payload["roles"] == roles
    assert payload["permissions"] == permissions
    assert payload["org_id"] == org_id
    assert "jti" in payload


def test_refresh_token_creation():
    subject = "user-999"
    token, jti = create_refresh_token(subject=subject, expires_delta=timedelta(days=7))

    assert isinstance(token, str)
    assert isinstance(jti, str)

    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_token_expiration_rejection():
    # Token with negative expiry (already expired)
    expired_token = create_access_token(
        subject="user-1",
        roles=[],
        permissions=[],
        expires_delta=timedelta(seconds=-1),
    )
    with pytest.raises(JWTError):
        decode_token(expired_token)


def test_audit_checksum_tamper_detection():
    actor = "10"
    action = "INCIDENT_VERIFY"
    entity_type = "Incident"
    entity_id = "RSQ-101"
    timestamp = "1791047420"
    details = '{"status": "VERIFIED", "severity": "HIGH"}'

    valid_checksum = compute_audit_checksum(
        actor_id=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        timestamp_iso=timestamp,
        details_str=details,
    )
    assert isinstance(valid_checksum, str)
    assert len(valid_checksum) == 64  # SHA-256 hex string

    # Altering details must change checksum
    tampered_details = '{"status": "REJECTED", "severity": "LOW"}'
    tampered_checksum = compute_audit_checksum(
        actor_id=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        timestamp_iso=timestamp,
        details_str=tampered_details,
    )
    assert valid_checksum != tampered_checksum
