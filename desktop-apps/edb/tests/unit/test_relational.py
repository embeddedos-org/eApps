"""Unit tests for the relational (SQL) store."""

from edb.core.models import ColumnDefinition, ColumnType, TableSchema
from edb.core.relational import RelationalStore


def test_create_table(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT, nullable=False),
            ColumnDefinition(name="email", col_type=ColumnType.TEXT, unique=True),
        ],
    )
    store.create_table(schema)
    assert engine.table_exists("users")


def test_insert_and_select(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="products",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
            ColumnDefinition(name="price", col_type=ColumnType.REAL),
        ],
    )
    store.create_table(schema)

    result = store.insert("products", {"id": 1, "name": "Widget", "price": 9.99})
    assert result.affected_rows == 1
    assert result.last_row_id == 1

    result = store.select("products")
    assert result.row_count == 1
    assert result.rows[0]["name"] == "Widget"
    assert result.rows[0]["price"] == 9.99


def test_insert_many(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="items",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
        ],
    )
    store.create_table(schema)

    rows = [{"id": i, "name": f"item_{i}"} for i in range(1, 6)]
    result = store.insert_many("items", rows)
    assert result.affected_rows == 5

    result = store.select("items")
    assert result.row_count == 5


def test_select_with_where(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
            ColumnDefinition(name="age", col_type=ColumnType.INTEGER),
        ],
    )
    store.create_table(schema)
    store.insert("users", {"id": 1, "name": "Alice", "age": 30})
    store.insert("users", {"id": 2, "name": "Bob", "age": 25})

    result = store.select("users", where={"name": "Alice"})
    assert result.row_count == 1
    assert result.rows[0]["age"] == 30


def test_select_with_limit_offset(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="nums",
        columns=[
            ColumnDefinition(name="val", col_type=ColumnType.INTEGER),
        ],
    )
    store.create_table(schema)
    for i in range(10):
        store.insert("nums", {"val": i})

    result = store.select("nums", limit=3, offset=2)
    assert result.row_count == 3


def test_update(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
        ],
    )
    store.create_table(schema)
    store.insert("users", {"id": 1, "name": "Alice"})

    result = store.update("users", {"name": "Alicia"}, {"id": 1})
    assert result.affected_rows == 1

    result = store.select("users", where={"id": 1})
    assert result.rows[0]["name"] == "Alicia"


def test_delete(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
        ],
    )
    store.create_table(schema)
    store.insert("users", {"id": 1, "name": "Alice"})
    store.insert("users", {"id": 2, "name": "Bob"})

    result = store.delete("users", {"id": 1})
    assert result.affected_rows == 1

    result = store.select("users")
    assert result.row_count == 1
    assert result.rows[0]["name"] == "Bob"


def test_list_tables(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="table_a",
        columns=[ColumnDefinition(name="id", col_type=ColumnType.INTEGER)],
    )
    store.create_table(schema)
    schema.name = "table_b"
    store.create_table(schema)

    tables = store.list_tables()
    assert "table_a" in tables
    assert "table_b" in tables


def test_drop_table(engine):
    store = RelationalStore(engine)
    schema = TableSchema(
        name="temp_table",
        columns=[ColumnDefinition(name="id", col_type=ColumnType.INTEGER)],
    )
    store.create_table(schema)
    assert engine.table_exists("temp_table")

    store.drop_table("temp_table")
    assert not engine.table_exists("temp_table")


def test_execute_raw(engine):
    store = RelationalStore(engine)
    store.execute_raw("CREATE TABLE raw_test (id INTEGER, val TEXT)")
    store.execute_raw("INSERT INTO raw_test VALUES (?, ?)", (1, "hello"))

    result = store.execute_raw("SELECT * FROM raw_test")
    assert result.row_count == 1
    assert result.rows[0]["val"] == "hello"
