"""Unit tests for JWT authentication."""

from edb.auth.jwt_handler import JWTHandler


def test_create_and_verify_access_token():
    handler = JWTHandler(secret_key="test-secret")
    token = handler.create_access_token("user-1", "alice", "admin")

    payload = handler.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["username"] == "alice"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_create_and_verify_refresh_token():
    handler = JWTHandler(secret_key="test-secret")
    token = handler.create_refresh_token("user-1")

    payload = handler.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["type"] == "refresh"


def test_invalid_token():
    handler = JWTHandler(secret_key="test-secret")
    payload = handler.verify_token("invalid.token.here")
    assert payload is None


def test_wrong_secret():
    handler1 = JWTHandler(secret_key="secret-1")
    handler2 = JWTHandler(secret_key="secret-2")

    token = handler1.create_access_token("user-1", "alice", "admin")
    payload = handler2.verify_token(token)
    assert payload is None


def test_token_pair():
    handler = JWTHandler(secret_key="test-secret")
    pair = handler.create_token_pair("user-1", "alice", "admin")

    assert "access_token" in pair
    assert "refresh_token" in pair
    assert pair["token_type"] == "bearer"

    access_payload = handler.verify_token(pair["access_token"])
    assert access_payload["type"] == "access"

    refresh_payload = handler.verify_token(pair["refresh_token"])
    assert refresh_payload["type"] == "refresh"
