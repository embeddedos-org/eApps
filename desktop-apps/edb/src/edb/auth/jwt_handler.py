"""JWT token handler for eDB authentication.

Manages creation and verification of access and refresh tokens.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt


class JWTHandler:
    """Handles JWT token creation and verification."""

    def __init__(
        self,
        secret_key: str = "edb-secret-change-me-in-production",
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._secret = secret_key
        self._algorithm = algorithm
        self._access_expire = access_token_expire_minutes
        self._refresh_expire = refresh_token_expire_days

    def create_access_token(
        self,
        user_id: str,
        username: str,
        role: str,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create a JWT access token."""
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self._access_expire),
        }
        if extra_claims:
            reserved = {"sub", "exp", "iat", "type", "username", "role"}
            safe_claims = {k: v for k, v in extra_claims.items() if k not in reserved}
            payload.update(safe_claims)
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: str) -> str:
        """Create a JWT refresh token."""
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self._refresh_expire),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode a JWT token. Returns payload or None if invalid/expired."""
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def decode_expired_token(self, token: str) -> dict[str, Any] | None:
        """Decode a token without verifying expiration (for refresh flow)."""
        try:
            payload = jwt.decode(
                token, self._secret, algorithms=[self._algorithm],
                options={"verify_exp": False}
            )
            return payload
        except jwt.InvalidTokenError:
            return None

    def create_token_pair(
        self,
        user_id: str,
        username: str,
        role: str,
    ) -> dict[str, str]:
        """Create both access and refresh tokens."""
        return {
            "access_token": self.create_access_token(user_id, username, role),
            "refresh_token": self.create_refresh_token(user_id),
            "token_type": "bearer",
            "expires_in": self._access_expire * 60,
        }

    @property
    def access_expire_minutes(self) -> int:
        return self._access_expire
