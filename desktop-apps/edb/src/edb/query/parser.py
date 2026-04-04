"""Query parser for eDB's JSON-based query DSL.

Parses incoming query dictionaries into typed query objects
that the planner can route to the correct store.
"""

from __future__ import annotations

from typing import Any, ClassVar

from edb.query.models import (
    DocumentQuery,
    KVQuery,
    QueryType,
    SQLQuery,
    UnifiedQuery,
)


class QueryParser:
    """Parses JSON/dict queries into typed query objects."""

    VALID_SQL_ACTIONS: ClassVar[set[str]] = {
        "select", "insert", "update", "delete", "raw",
        "create_table", "drop_table",
    }
    VALID_DOC_ACTIONS: ClassVar[set[str]] = {
        "find", "find_by_id", "insert", "update", "delete",
        "count", "list_collections",
    }
    VALID_KV_ACTIONS: ClassVar[set[str]] = {"get", "set", "delete", "list", "exists", "count"}

    def parse(self, query_dict: dict[str, Any]) -> UnifiedQuery:
        """Parse a raw query dict into a UnifiedQuery.

        Expected format:
            {"type": "sql|document|kv", ...type-specific fields}
        """
        query_type = self._resolve_type(query_dict)

        if query_type == QueryType.SQL:
            return self._parse_sql(query_dict)
        elif query_type == QueryType.DOCUMENT:
            return self._parse_document(query_dict)
        elif query_type == QueryType.KV:
            return self._parse_kv(query_dict)
        else:
            raise QueryParseError(f"Unknown query type: {query_dict.get('type')}")

    def _resolve_type(self, query_dict: dict[str, Any]) -> QueryType:
        raw_type = query_dict.get("type", "").lower()
        type_map = {
            "sql": QueryType.SQL,
            "relational": QueryType.SQL,
            "document": QueryType.DOCUMENT,
            "doc": QueryType.DOCUMENT,
            "nosql": QueryType.DOCUMENT,
            "kv": QueryType.KV,
            "key_value": QueryType.KV,
            "keyvalue": QueryType.KV,
        }
        if raw_type not in type_map:
            raise QueryParseError(
                f"Invalid query type '{raw_type}'. "
                f"Valid types: {', '.join(type_map.keys())}"
            )
        return type_map[raw_type]

    def _parse_sql(self, q: dict[str, Any]) -> UnifiedQuery:
        action = q.get("action", "").lower()
        if action not in self.VALID_SQL_ACTIONS:
            raise QueryParseError(
                f"Invalid SQL action '{action}'. Valid: {self.VALID_SQL_ACTIONS}"
            )
        if action != "raw" and not q.get("table"):
            raise QueryParseError("SQL queries require a 'table' field")

        sql_query = SQLQuery(
            action=action,
            table=q.get("table", ""),
            columns=q.get("columns"),
            data=q.get("data"),
            where=q.get("where"),
            order_by=q.get("order_by"),
            limit=q.get("limit"),
            offset=q.get("offset"),
            raw_sql=q.get("raw_sql"),
            params=q.get("params"),
        )
        return UnifiedQuery(type=QueryType.SQL, sql=sql_query)

    def _parse_document(self, q: dict[str, Any]) -> UnifiedQuery:
        action = q.get("action", "").lower()
        if action not in self.VALID_DOC_ACTIONS:
            raise QueryParseError(
                f"Invalid document action '{action}'. Valid: {self.VALID_DOC_ACTIONS}"
            )
        if action != "list_collections" and not q.get("collection"):
            raise QueryParseError("Document queries require a 'collection' field")

        doc_query = DocumentQuery(
            action=action,
            collection=q.get("collection", ""),
            data=q.get("data"),
            filter=q.get("filter"),
            doc_id=q.get("doc_id"),
            merge=q.get("merge", True),
            limit=q.get("limit"),
            offset=q.get("offset"),
        )
        return UnifiedQuery(type=QueryType.DOCUMENT, document=doc_query)

    def _parse_kv(self, q: dict[str, Any]) -> UnifiedQuery:
        action = q.get("action", "").lower()
        if action not in self.VALID_KV_ACTIONS:
            raise QueryParseError(
                f"Invalid KV action '{action}'. Valid: {self.VALID_KV_ACTIONS}"
            )

        kv_query = KVQuery(
            action=action,
            key=q.get("key"),
            value=q.get("value"),
            ttl=q.get("ttl"),
            prefix=q.get("prefix"),
        )
        return UnifiedQuery(type=QueryType.KV, kv=kv_query)


class QueryParseError(Exception):
    """Raised when a query cannot be parsed."""
