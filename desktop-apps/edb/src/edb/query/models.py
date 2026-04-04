"""Query models for eDB's JSON-based query DSL."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class QueryType(StrEnum):
    """Type of query to execute."""
    SQL = "sql"
    DOCUMENT = "document"
    KV = "kv"


class SQLQuery(BaseModel):
    """A SQL-style query."""
    type: QueryType = QueryType.SQL
    action: str  # select, insert, update, delete, raw
    table: str
    columns: list[str] | None = None
    data: dict[str, Any] | None = None
    where: dict[str, Any] | None = None
    order_by: str | None = None
    limit: int | None = None
    offset: int | None = None
    raw_sql: str | None = None
    params: list[Any] | None = None


class DocumentQuery(BaseModel):
    """A document store query."""
    type: QueryType = QueryType.DOCUMENT
    action: str  # find, insert, update, delete, count
    collection: str
    data: dict[str, Any] | None = None
    filter: dict[str, Any] | None = None
    doc_id: str | None = None
    merge: bool = True
    limit: int | None = None
    offset: int | None = None


class KVQuery(BaseModel):
    """A key-value store query."""
    type: QueryType = QueryType.KV
    action: str  # get, set, delete, list, exists
    key: str | None = None
    value: Any = None
    ttl: int | None = None
    prefix: str | None = None


class UnifiedQuery(BaseModel):
    """A unified query that wraps all query types."""
    type: QueryType
    sql: SQLQuery | None = None
    document: DocumentQuery | None = None
    kv: KVQuery | None = None


class UnifiedQueryResult(BaseModel):
    """Unified result from any query type."""
    success: bool = True
    query_type: QueryType
    data: Any = None
    error: str | None = None
    row_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
