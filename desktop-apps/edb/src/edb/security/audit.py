"""Tamper-resistant audit logging for eDB.

Records all queries, auth events, and admin actions with hash-chain
verification to detect tampering.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from edb.core.engine import StorageEngine

AUDIT_TABLE = "_edb_audit_log"


class AuditLogger:
    """Append-only audit log with hash chain verification."""

    def __init__(self, engine: StorageEngine) -> None:
        self._engine = engine
        self._ensure_table()

    def _ensure_table(self) -> None:
        self._engine.execute(f"""
            CREATE TABLE IF NOT EXISTS "{AUDIT_TABLE}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                username TEXT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                prev_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            )
        """)
        self._engine.commit()

    def log(
        self,
        event_type: str,
        action: str,
        user_id: str | None = None,
        username: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> int:
        """Log an audit event. Returns the entry ID."""
        timestamp = datetime.now(UTC).isoformat()
        details_json = json.dumps(details) if details else None
        prev_hash = self._get_last_hash()

        entry_data = f"{timestamp}|{event_type}|{user_id}|{action}|{details_json}|{prev_hash}"
        entry_hash = hashlib.sha256(entry_data.encode("utf-8")).hexdigest()

        cursor = self._engine.execute(
            f"""INSERT INTO "{AUDIT_TABLE}"
            (timestamp, event_type, user_id, username, action,
             details, ip_address, prev_hash, entry_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (timestamp, event_type, user_id, username, action, details_json, ip_address,
             prev_hash, entry_hash),
        )
        self._engine.commit()
        return cursor.lastrowid or 0

    def get_logs(
        self,
        event_type: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Retrieve audit log entries with optional filtering."""
        sql = f'SELECT * FROM "{AUDIT_TABLE}"'
        params: list[Any] = []
        conditions = []

        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self._engine.fetchall(sql, tuple(params))
        return [self._row_to_dict(row) for row in rows]

    def verify_chain(self) -> tuple[bool, str]:
        """Verify the integrity of the audit log hash chain.

        Returns (is_valid, message).
        """
        rows = self._engine.fetchall(
            f'SELECT * FROM "{AUDIT_TABLE}" ORDER BY id ASC'
        )
        if not rows:
            return True, "Audit log is empty"

        prev_hash = "genesis"
        for row in rows:
            details_str = row["details"]
            entry_data = (
                f"{row['timestamp']}|{row['event_type']}|{row['user_id']}|"
                f"{row['action']}|{details_str}|{prev_hash}"
            )
            expected_hash = hashlib.sha256(entry_data.encode("utf-8")).hexdigest()

            if row["prev_hash"] != prev_hash:
                return False, f"Chain broken at entry {row['id']}: prev_hash mismatch"
            if row["entry_hash"] != expected_hash:
                return False, f"Tampered entry detected at ID {row['id']}"

            prev_hash = row["entry_hash"]

        return True, f"Audit chain verified: {len(rows)} entries intact"

    def count(self) -> int:
        """Count total audit log entries."""
        row = self._engine.fetchone(f'SELECT COUNT(*) as cnt FROM "{AUDIT_TABLE}"')
        return row["cnt"] if row else 0

    def _get_last_hash(self) -> str:
        row = self._engine.fetchone(
            f'SELECT entry_hash FROM "{AUDIT_TABLE}" ORDER BY id DESC LIMIT 1'
        )
        return row["entry_hash"] if row else "genesis"

    def _row_to_dict(self, row: Any) -> dict[str, Any]:
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "user_id": row["user_id"],
            "username": row["username"],
            "action": row["action"],
            "details": json.loads(row["details"]) if row["details"] else None,
            "ip_address": row["ip_address"],
            "entry_hash": row["entry_hash"],
        }
