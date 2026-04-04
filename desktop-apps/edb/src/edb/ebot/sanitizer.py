"""Prompt sanitizer for ebot queries.

Validates translated queries and detects prompt injection attempts.
"""

from __future__ import annotations

from edb.ebot.models import TranslationResult
from edb.security.input_validation import InputValidator


class PromptSanitizer:
    """Sanitizes and validates ebot natural language queries and their translations."""

    def __init__(self) -> None:
        self._validator = InputValidator()

    def sanitize_input(self, text: str) -> tuple[str, list[str]]:
        """Sanitize user input text.

        Returns (sanitized_text, warnings).
        """
        warnings: list[str] = []

        if self._validator.check_prompt_injection(text):
            warnings.append("Potential prompt injection detected")

        if self._validator.check_sql_injection(text):
            warnings.append("Potential SQL injection in natural language query")

        sanitized = self._validator.sanitize_string(text, max_length=2000)
        return sanitized, warnings

    def validate_translation(
        self, result: TranslationResult, user_role: str = "read_only"
    ) -> TranslationResult:
        """Validate a translated query before execution.

        Checks for injection and enforces role-based restrictions.
        """
        if result.error or result.translated_query is None:
            return result

        query = result.translated_query
        warnings = self._validator.validate_query_input(query)
        if warnings:
            return TranslationResult(
                original_text=result.original_text,
                error=f"Unsafe translated query: {'; '.join(warnings)}",
            )

        action = query.get("action", "")
        write_actions = {"insert", "update", "delete", "drop_table", "set"}
        if action in write_actions and user_role == "read_only":
            return TranslationResult(
                original_text=result.original_text,
                error=f"Permission denied: '{action}' requires write access",
            )

        return result
