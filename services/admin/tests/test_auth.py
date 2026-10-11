import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth import create_access_token, decode_token, hash_password, verify_password
from app.config import get_settings


def test_password_roundtrip() -> None:
    hashed = hash_password("s3cret")
    assert hashed != "s3cret"
    assert verify_password("s3cret", hashed)
    assert not verify_password("wrong", hashed)


def test_token_roundtrip() -> None:
    claims = decode_token(create_access_token("admin"))
    assert claims["sub"] == "admin"
    assert "exp" in claims


def test_token_signed_with_another_key_is_rejected() -> None:
    forged = jwt.encode({"sub": "admin"}, "x" * 40, algorithm="HS256")
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(forged)


def test_token_requires_subject() -> None:
    token = jwt.encode({"foo": "bar"}, get_settings().jwt_secret, algorithm="HS256")
    with pytest.raises(jwt.MissingRequiredClaimError):
        decode_token(token)


def test_login_success_and_failure(client: TestClient) -> None:
    ok = client.post("/api/admin/login", json={"username": "admin", "password": "secret-pass"})
    assert ok.status_code == 200
    assert ok.json()["token_type"] == "bearer"
    bad = client.post("/api/admin/login", json={"username": "admin", "password": "nope"})
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "unauthorized"
