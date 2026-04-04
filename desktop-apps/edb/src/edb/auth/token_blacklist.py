"""Token blacklist for JWT revocation.

Stores revoked tokens to support logout and token invalidation.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from edb.core.engine import StorageEngine

BLACKLIST_TABLE = "_edb_token_blacklist"
logger = logging.getLogger("edb.auth.token_blacklist")


class TokenBlacklist:
    """Manages revoked JWT tokens."""

    def __init__(self, engine: StorageEngine) -> None:
        self._engine = engine
        self._ensure_table()

    def _ensure_table(self) -> None:
        self._engine.execute(f"""
            CREATE TABLE IF NOT EXISTS "{BLACKLIST_TABLE}" (
                token_jti TEXT PRIMARY KEY,
                user_id TEXT,
                revoked_at TEXT NOT NULL,
                expires_at TEXT
            )
        """)
        self._engine.commit()

    def revoke(self, token_jti: str, user_id: str | None = None, expires_at: str | None = None) -> None:
        """Add a token to the blacklist."""
        now = datetime.now(UTC).isoformat()
        self._engine.execute(
            f"""INSERT OR IGNORE INTO "{BLACKLIST_TABLE}" (token_jti, user_id, revoked_at, expires_at)
            VALUES (?, ?, ?, ?)""",
            (token_jti, user_id, now, expires_at),
        )
        self._engine.commit()
        logger.info("Token revoked: %s", token_jti[:16])

    def is_revoked(self, token_jti: str) -> bool:
        """Check if a token has been revoked."""
        row = self._engine.fetchone(
            f'SELECT token_jti FROM "{BLACKLIST_TABLE}" WHERE token_jti = ?',
            (token_jti,),
        )
        return row is not None

    def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke all tokens for a user. Returns count revoked."""
        now = datetime.now(UTC).isoformat()
        cursor = self._engine.execute(
            f"""INSERT OR IGNORE INTO "{BLACKLIST_TABLE}" (token_jti, user_id, revoked_at)
            VALUES (?, ?, ?)""",
            (f"user_revoke_{user_id}_{now}", user_id, now),
        )
        self._engine.commit()
        return cursor.rowcount

    def cleanup_expired(self) -> int:
        """Remove expired entries from the blacklist."""
        now = datetime.now(UTC).isoformat()
        cursor = self._engine.execute(
            f'DELETE FROM "{BLACKLIST_TABLE}" WHERE expires_at IS NOT NULL AND expires_at < ?',
            (now,),
        )
        self._engine.commit()
        return cursor.rowcount
