"""Unit tests for the query planner."""

from edb.core.models import ColumnDefinition, ColumnType, TableSchema
from edb.query.models import QueryType
from edb.query.parser import QueryParser
from edb.query.planner import QueryPlanner


def test_planner_sql_select(db):
    schema = TableSchema(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
        ],
    )
    db.sql.create_table(schema)
    db.sql.insert("users", {"id": 1, "name": "Alice"})

    parser = QueryParser()
    planner = QueryPlanner(db)

    query = parser.parse({"type": "sql", "action": "select", "table": "users"})
    result = planner.execute(query)

    assert result.success
    assert result.query_type == QueryType.SQL
    assert len(result.data) == 1
    assert result.data[0]["name"] == "Alice"


def test_planner_sql_insert(db):
    schema = TableSchema(
        name="items",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
        ],
    )
    db.sql.create_table(schema)

    parser = QueryParser()
    planner = QueryPlanner(db)

    query = parser.parse({
        "type": "sql", "action": "insert", "table": "items",
        "data": {"id": 1, "name": "Widget"},
    })
    result = planner.execute(query)

    assert result.success
    assert result.data["last_row_id"] == 1


def test_planner_document_insert_and_find(db):
    parser = QueryParser()
    planner = QueryPlanner(db)

    insert_q = parser.parse({
        "type": "document", "action": "insert", "collection": "logs",
        "data": {"event": "login", "user": "alice"},
    })
    result = planner.execute(insert_q)
    assert result.success

    find_q = parser.parse({
        "type": "document", "action": "find", "collection": "logs",
        "filter": {"event": "login"},
    })
    result = planner.execute(find_q)
    assert result.success
    assert result.row_count == 1


def test_planner_kv_set_and_get(db):
    parser = QueryParser()
    planner = QueryPlanner(db)

    set_q = parser.parse({
        "type": "kv", "action": "set", "key": "config", "value": {"theme": "dark"},
    })
    result = planner.execute(set_q)
    assert result.success

    get_q = parser.parse({"type": "kv", "action": "get", "key": "config"})
    result = planner.execute(get_q)
    assert result.success
    assert result.data == {"theme": "dark"}


def test_planner_error_handling(db):
    parser = QueryParser()
    planner = QueryPlanner(db)

    query = parser.parse({
        "type": "sql", "action": "select", "table": "nonexistent_table",
    })
    result = planner.execute(query)
    assert not result.success
    assert result.error is not None
