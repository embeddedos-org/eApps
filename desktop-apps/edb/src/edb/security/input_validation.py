"""Input validation and sanitization for eDB.

Protects against SQL injection, NoSQL injection, command injection,
and prompt injection attacks.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar


class InputValidator:
    """Validates and sanitizes input for all eDB interfaces."""

    SQL_INJECTION_PATTERNS: ClassVar[list[str]] = [
        r";\s*DROP\s+",
        r";\s*DELETE\s+",
        r";\s*UPDATE\s+",
        r";\s*INSERT\s+",
        r";\s*ALTER\s+",
        r"'\s*OR\s+'1'\s*=\s*'1",
        r"'\s*OR\s+1\s*=\s*1",
        r"--\s*$",
        r"/\*.*\*/",
        r"UNION\s+SELECT",
        r"EXEC(\s+|\()",
        r"xp_cmdshell",
    ]

    NOSQL_INJECTION_PATTERNS: ClassVar[list[str]] = [
        r"\$where\b",
        r"\$ne\b",
        r"\$gt\b",
        r"\$lt\b",
        r"\$regex\b",
        r"\$exists\b",
    ]

    PROMPT_INJECTION_PATTERNS: ClassVar[list[str]] = [
        r"ignore\s+(previous|above|all)\s+(instructions|prompts)",
        r"disregard\s+(previous|above|all)",
        r"forget\s+(everything|your\s+instructions)",
        r"you\s+are\s+now\s+",
        r"act\s+as\s+(a|an)\s+",
        r"system\s*:\s*",
        r"<\s*script\b",
        r"javascript\s*:",
    ]

    def validate_table_name(self, name: str) -> bool:
        """Validate a table/collection name."""
        if not name or not isinstance(name, str):
            return False
        return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$", name))

    def validate_column_name(self, name: str) -> bool:
        """Validate a column name."""
        return self.validate_table_name(name)

    def check_sql_injection(self, value: str) -> bool:
        """Check if a string contains SQL injection patterns.

        Returns True if injection detected.
        """
        if not isinstance(value, str):
            return False
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    def check_nosql_injection(self, value: Any) -> bool:
        """Check if a value contains NoSQL injection patterns.

        Returns True if injection detected.
        """
        if isinstance(value, str):
            for pattern in self.NOSQL_INJECTION_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    return True
        elif isinstance(value, dict):
            for k, v in value.items():
                if self.check_nosql_injection(k) or self.check_nosql_injection(v):
                    return True
        elif isinstance(value, list):
            for item in value:
                if self.check_nosql_injection(item):
                    return True
        return False

    def check_prompt_injection(self, text: str) -> bool:
        """Check if text contains prompt injection patterns.

        Returns True if injection detected.
        """
        if not isinstance(text, str):
            return False
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def sanitize_string(self, value: str, max_length: int = 10000) -> str:
        """Sanitize a string by removing dangerous characters."""
        if not isinstance(value, str):
            return ""
        value = value[:max_length]
        value = value.replace("\x00", "")
        return value

    def validate_query_input(self, query_dict: dict[str, Any]) -> list[str]:
        """Validate an entire query dict for injection attacks.

        Returns a list of warning messages (empty if clean).
        """
        warnings = []
        self._check_dict_recursive(query_dict, warnings, "query")
        return warnings

    def _check_dict_recursive(
        self, data: Any, warnings: list[str], path: str
    ) -> None:
        if isinstance(data, str):
            if self.check_sql_injection(data):
                warnings.append(f"Potential SQL injection at {path}: {data[:50]}")
            if self.check_nosql_injection(data):
                warnings.append(f"Potential NoSQL injection at {path}: {data[:50]}")
        elif isinstance(data, dict):
            for key, value in data.items():
                self._check_dict_recursive(value, warnings, f"{path}.{key}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._check_dict_recursive(item, warnings, f"{path}[{i}]")
