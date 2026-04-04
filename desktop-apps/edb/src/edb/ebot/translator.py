"""Natural language to query translation for ebot.

Uses a rule-based approach by default, with an optional LLM backend.
"""

from __future__ import annotations

import re
from typing import Any

from edb.ebot.models import TranslationResult


class NLQueryTranslator:
    """Translates natural language queries into eDB query DSL."""

    def __init__(self, provider: str = "rule_based", **kwargs: Any) -> None:
        self._provider = provider
        self._kwargs = kwargs

    def translate(self, text: str, context: dict[str, Any] | None = None) -> TranslationResult:
        """Translate a natural language query to eDB query DSL."""
        text = text.strip()
        if not text:
            return TranslationResult(
                original_text=text, error="Empty query"
            )

        if self._provider == "rule_based":
            return self._rule_based_translate(text, context)
        else:
            return TranslationResult(
                original_text=text,
                error=f"Provider '{self._provider}' not available. Use 'rule_based'.",
            )

    def _rule_based_translate(
        self, text: str, context: dict[str, Any] | None = None
    ) -> TranslationResult:
        """Rule-based translation using regex patterns."""
        text_lower = text.lower().strip()

        # "list tables/collections/keys" → metadata queries (must be checked before generic pattern)
        if "list tables" in text_lower or "show tables" in text_lower:
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "sql",
                    "action": "raw",
                    "raw_sql": "SELECT name FROM sqlite_master WHERE type='table'",
                },
                confidence=0.9,
                explanation="List all tables",
            )

        if "list collections" in text_lower:
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "document",
                    "action": "list_collections",
                    "collection": "",
                },
                confidence=0.9,
                explanation="List all document collections",
            )

        if "list keys" in text_lower:
            return TranslationResult(
                original_text=text,
                translated_query={"type": "kv", "action": "list"},
                confidence=0.9,
                explanation="List all keys",
            )

        # "show all/list <table>" → SELECT
        match = re.match(
            r"(?:show|list|get|display|find)\s+(?:all\s+)?(?:from\s+)?(\w+)",
            text_lower,
        )
        if match:
            table = match.group(1)
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "sql",
                    "action": "select",
                    "table": table,
                },
                confidence=0.7,
                explanation=f"SELECT all from '{table}'",
            )

        # "count <collection/table>" → COUNT
        match = re.match(r"(?:count|how many)\s+(\w+)", text_lower)
        if match:
            target = match.group(1)
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "document",
                    "action": "count",
                    "collection": target,
                },
                confidence=0.6,
                explanation=f"Count documents in '{target}'",
            )

        # "insert/add <data> into <table>" → INSERT
        match = re.match(
            r"(?:insert|add|create)\s+(.+?)\s+(?:into|to|in)\s+(\w+)",
            text_lower,
        )
        if match:
            data_str = match.group(1)
            table = match.group(2)
            data = self._parse_simple_data(data_str)
            if data:
                return TranslationResult(
                    original_text=text,
                    translated_query={
                        "type": "sql",
                        "action": "insert",
                        "table": table,
                        "data": data,
                    },
                    confidence=0.5,
                    explanation=f"INSERT into '{table}'",
                )

        # "delete from <table> where <key>=<value>" → DELETE
        match = re.match(
            r"(?:delete|remove)\s+(?:from\s+)?(\w+)\s+where\s+(\w+)\s*=\s*['\"]?(.+?)['\"]?\s*$",
            text_lower,
        )
        if match:
            table = match.group(1)
            key = match.group(2)
            value = match.group(3)
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "sql",
                    "action": "delete",
                    "table": table,
                    "where": {key: value},
                },
                confidence=0.6,
                explanation=f"DELETE from '{table}' where {key}={value}",
            )

        # "find <collection> where <key>=<value>" → DOCUMENT FIND
        match = re.match(
            r"find\s+(?:in\s+)?(\w+)\s+where\s+(\w+)\s*=\s*['\"]?(.+?)['\"]?\s*$",
            text_lower,
        )
        if match:
            collection = match.group(1)
            key = match.group(2)
            value = match.group(3)
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "document",
                    "action": "find",
                    "collection": collection,
                    "filter": {key: value},
                },
                confidence=0.6,
                explanation=f"Find in '{collection}' where {key}={value}",
            )

        # "get key <key>" → KV GET
        match = re.match(r"get\s+(?:key\s+)?['\"]?(.+?)['\"]?\s*$", text_lower)
        if match:
            key = match.group(1)
            return TranslationResult(
                original_text=text,
                translated_query={
                    "type": "kv",
                    "action": "get",
                    "key": key,
                },
                confidence=0.5,
                explanation=f"GET key '{key}'",
            )

        # "list tables/collections/keys" → metadata queries
        # (already handled at the top of the method; this is unreachable)

        return TranslationResult(
            original_text=text,
            error=(
                "Could not understand the query. Try:"
                " 'show all users', 'count orders', 'list tables'"
            ),
        )

    def _parse_simple_data(self, data_str: str) -> dict[str, str] | None:
        """Parse simple key=value pairs from a string."""
        pairs = re.findall(r"(\w+)\s*=\s*['\"]?([^,'\"\s]+)['\"]?", data_str)
        if pairs:
            return dict(pairs)
        return None
