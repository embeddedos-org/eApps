"""Unit tests for the query parser."""

import pytest

from edb.query.models import QueryType
from edb.query.parser import QueryParseError, QueryParser


@pytest.fixture
def parser():
    return QueryParser()


def test_parse_sql_select(parser):
    query = parser.parse({"type": "sql", "action": "select", "table": "users"})
    assert query.type == QueryType.SQL
    assert query.sql.action == "select"
    assert query.sql.table == "users"


def test_parse_sql_insert(parser):
    query = parser.parse({
        "type": "sql",
        "action": "insert",
        "table": "users",
        "data": {"name": "Alice"},
    })
    assert query.sql.action == "insert"
    assert query.sql.data == {"name": "Alice"}


def test_parse_document_find(parser):
    query = parser.parse({
        "type": "document",
        "action": "find",
        "collection": "logs",
        "filter": {"level": "error"},
    })
    assert query.type == QueryType.DOCUMENT
    assert query.document.action == "find"
    assert query.document.filter == {"level": "error"}


def test_parse_kv_get(parser):
    query = parser.parse({"type": "kv", "action": "get", "key": "config"})
    assert query.type == QueryType.KV
    assert query.kv.action == "get"
    assert query.kv.key == "config"


def test_parse_type_aliases(parser):
    for alias in ["relational", "sql"]:
        query = parser.parse({"type": alias, "action": "select", "table": "t"})
        assert query.type == QueryType.SQL

    for alias in ["doc", "nosql", "document"]:
        query = parser.parse({"type": alias, "action": "find", "collection": "c"})
        assert query.type == QueryType.DOCUMENT

    for alias in ["kv", "key_value", "keyvalue"]:
        query = parser.parse({"type": alias, "action": "get", "key": "k"})
        assert query.type == QueryType.KV


def test_parse_invalid_type(parser):
    with pytest.raises(QueryParseError, match="Invalid query type"):
        parser.parse({"type": "invalid", "action": "select"})


def test_parse_invalid_action(parser):
    with pytest.raises(QueryParseError, match="Invalid SQL action"):
        parser.parse({"type": "sql", "action": "invalid", "table": "t"})


def test_parse_missing_table(parser):
    with pytest.raises(QueryParseError, match="require a 'table' field"):
        parser.parse({"type": "sql", "action": "select"})


def test_parse_raw_sql_no_table(parser):
    query = parser.parse({
        "type": "sql",
        "action": "raw",
        "raw_sql": "SELECT 1",
    })
    assert query.sql.action == "raw"
    assert query.sql.raw_sql == "SELECT 1"
