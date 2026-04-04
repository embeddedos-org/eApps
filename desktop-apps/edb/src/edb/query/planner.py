"""Query planner for eDB — routes parsed queries to the appropriate store."""

from __future__ import annotations

from edb.core.database import Database
from edb.core.models import ColumnDefinition, TableSchema
from edb.query.models import (
    DocumentQuery,
    KVQuery,
    QueryType,
    SQLQuery,
    UnifiedQuery,
    UnifiedQueryResult,
)


class QueryPlanner:
    """Routes parsed queries to the correct store and executes them."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def execute(self, query: UnifiedQuery) -> UnifiedQueryResult:
        """Execute a unified query and return the result."""
        try:
            if query.type == QueryType.SQL and query.sql:
                return self._execute_sql(query.sql)
            elif query.type == QueryType.DOCUMENT and query.document:
                return self._execute_document(query.document)
            elif query.type == QueryType.KV and query.kv:
                return self._execute_kv(query.kv)
            else:
                return UnifiedQueryResult(
                    success=False,
                    query_type=query.type,
                    error="Invalid query: missing type-specific query data",
                )
        except Exception as e:
            return UnifiedQueryResult(
                success=False,
                query_type=query.type,
                error=str(e),
            )

    def _execute_sql(self, q: SQLQuery) -> UnifiedQueryResult:
        store = self._db.sql

        if q.action == "select":
            rows = store.select(
                table=q.table,
                columns=q.columns,
                where=q.where,
                order_by=q.order_by,
                limit=q.limit,
                offset=q.offset,
            )
            columns = list(rows[0].keys()) if rows else []
            return UnifiedQueryResult(
                query_type=QueryType.SQL,
                data=rows,
                row_count=len(rows),
                metadata={"columns": columns},
            )

        elif q.action == "insert":
            if not q.data:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.SQL,
                    error="Insert requires 'data'",
                )
            last_row_id = store.insert(q.table, q.data)
            return UnifiedQueryResult(
                query_type=QueryType.SQL,
                data={"last_row_id": last_row_id},
                row_count=1,
            )

        elif q.action == "update":
            if not q.data or not q.where:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.SQL,
                    error="Update requires 'data' and 'where'",
                )
            affected = store.update(q.table, q.data, q.where)
            return UnifiedQueryResult(
                query_type=QueryType.SQL,
                row_count=affected,
            )

        elif q.action == "delete":
            if not q.where:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.SQL,
                    error="Delete requires 'where'",
                )
            deleted = store.delete(q.table, q.where)
            return UnifiedQueryResult(
                query_type=QueryType.SQL,
                row_count=deleted,
            )

        elif q.action == "raw":
            if not q.raw_sql:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.SQL,
                    error="Raw query requires 'raw_sql'",
                )
            params = tuple(q.params) if q.params else None
            result = store.execute_raw(q.raw_sql, params)
            return UnifiedQueryResult(
                query_type=QueryType.SQL,
                data=result.rows if result.rows else None,
                row_count=result.row_count or result.affected_rows,
                metadata={"columns": result.columns},
            )

        elif q.action == "create_table":
            if not q.data or "columns" not in q.data:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.SQL,
                    error="create_table requires 'data' with 'columns' list",
                )
            columns = [ColumnDefinition(**col) for col in q.data["columns"]]
            schema = TableSchema(name=q.table, columns=columns)
            store.create_table(schema)
            return UnifiedQueryResult(query_type=QueryType.SQL, data={"table_created": q.table})

        elif q.action == "drop_table":
            store.drop_table(q.table)
            return UnifiedQueryResult(query_type=QueryType.SQL, data={"table_dropped": q.table})

        return UnifiedQueryResult(
            success=False, query_type=QueryType.SQL, error=f"Unknown SQL action: {q.action}"
        )

    def _execute_document(self, q: DocumentQuery) -> UnifiedQueryResult:
        store = self._db.docs

        if q.action == "find":
            docs = store.find(
                collection=q.collection,
                filter_dict=q.filter,
                limit=q.limit,
                offset=q.offset,
            )
            return UnifiedQueryResult(
                query_type=QueryType.DOCUMENT,
                data=[d.model_dump(mode="json") for d in docs],
                row_count=len(docs),
            )

        elif q.action == "find_by_id":
            if not q.doc_id:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.DOCUMENT,
                    error="find_by_id requires 'doc_id'",
                )
            doc = store.find_by_id(q.collection, q.doc_id)
            if doc:
                return UnifiedQueryResult(
                    query_type=QueryType.DOCUMENT,
                    data=doc.model_dump(mode="json"),
                    row_count=1,
                )
            return UnifiedQueryResult(
                query_type=QueryType.DOCUMENT, data=None, row_count=0
            )

        elif q.action == "insert":
            if not q.data:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.DOCUMENT,
                    error="Insert requires 'data'",
                )
            doc = store.insert(q.collection, q.data, q.doc_id)
            return UnifiedQueryResult(
                query_type=QueryType.DOCUMENT,
                data=doc.model_dump(mode="json"),
                row_count=1,
            )

        elif q.action == "update":
            if not q.doc_id or not q.data:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.DOCUMENT,
                    error="Update requires 'doc_id' and 'data'",
                )
            doc = store.update(q.collection, q.doc_id, q.data, q.merge)
            if doc:
                return UnifiedQueryResult(
                    query_type=QueryType.DOCUMENT,
                    data=doc.model_dump(mode="json"),
                    row_count=1,
                )
            return UnifiedQueryResult(
                success=False, query_type=QueryType.DOCUMENT, error="Document not found"
            )

        elif q.action == "delete":
            if not q.doc_id:
                return UnifiedQueryResult(
                    success=False,
                    query_type=QueryType.DOCUMENT,
                    error="Delete requires 'doc_id'",
                )
            deleted = store.delete(q.collection, q.doc_id)
            return UnifiedQueryResult(
                query_type=QueryType.DOCUMENT,
                data={"deleted": deleted},
                row_count=1 if deleted else 0,
            )

        elif q.action == "count":
            cnt = store.count(q.collection, q.filter)
            return UnifiedQueryResult(
                query_type=QueryType.DOCUMENT, data={"count": cnt}, row_count=cnt
            )

        elif q.action == "list_collections":
            collections = store.list_collections()
            return UnifiedQueryResult(
                query_type=QueryType.DOCUMENT,
                data=collections,
                row_count=len(collections),
            )

        return UnifiedQueryResult(
            success=False,
            query_type=QueryType.DOCUMENT,
            error=f"Unknown document action: {q.action}",
        )

    def _execute_kv(self, q: KVQuery) -> UnifiedQueryResult:
        store = self._db.kv

        if q.action == "get":
            if not q.key:
                return UnifiedQueryResult(
                    success=False, query_type=QueryType.KV, error="Get requires 'key'"
                )
            value = store.get(q.key)
            return UnifiedQueryResult(
                query_type=QueryType.KV,
                data=value,
                row_count=1 if value is not None else 0,
            )

        elif q.action == "set":
            if not q.key:
                return UnifiedQueryResult(
                    success=False, query_type=QueryType.KV, error="Set requires 'key'"
                )
            entry = store.set(q.key, q.value, q.ttl)
            return UnifiedQueryResult(
                query_type=QueryType.KV,
                data=entry.model_dump(mode="json"),
                row_count=1,
            )

        elif q.action == "delete":
            if not q.key:
                return UnifiedQueryResult(
                    success=False, query_type=QueryType.KV, error="Delete requires 'key'"
                )
            deleted = store.delete(q.key)
            return UnifiedQueryResult(
                query_type=QueryType.KV,
                data={"deleted": deleted},
                row_count=1 if deleted else 0,
            )

        elif q.action == "list":
            keys = store.list_keys(q.prefix)
            return UnifiedQueryResult(
                query_type=QueryType.KV, data=keys, row_count=len(keys)
            )

        elif q.action == "exists":
            if not q.key:
                return UnifiedQueryResult(
                    success=False, query_type=QueryType.KV, error="Exists requires 'key'"
                )
            exists = store.exists(q.key)
            return UnifiedQueryResult(
                query_type=QueryType.KV, data={"exists": exists}, row_count=1
            )

        elif q.action == "count":
            cnt = store.count()
            return UnifiedQueryResult(
                query_type=QueryType.KV, data={"count": cnt}, row_count=cnt
            )

        return UnifiedQueryResult(
            success=False, query_type=QueryType.KV, error=f"Unknown KV action: {q.action}"
        )
