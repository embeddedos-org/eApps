"""Unit tests for the unified Database class."""

from edb.core.database import Database
from edb.core.models import ColumnDefinition, ColumnType, TableSchema


def test_database_context_manager(tmp_db_path):
    with Database(tmp_db_path) as db:
        db.kv.set("test", "value")
        assert db.kv.get("test") == "value"


def test_database_multi_model(db):
    schema = TableSchema(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT),
        ],
    )
    db.sql.create_table(schema)
    db.sql.insert("users", {"id": 1, "name": "Alice"})

    db.docs.insert("logs", {"event": "user_created", "user_id": 1})

    db.kv.set("user:1:session", {"active": True})

    sql_result = db.sql.select("users", where={"id": 1})
    assert sql_result.rows[0]["name"] == "Alice"

    doc_result = db.docs.find("logs", filter_dict={"event": "user_created"})
    assert len(doc_result) == 1

    kv_result = db.kv.get("user:1:session")
    assert kv_result["active"] is True


def test_transaction_commit(db):
    schema = TableSchema(
        name="accounts",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="balance", col_type=ColumnType.REAL),
        ],
    )
    db.sql.create_table(schema)
    db.sql.insert("accounts", {"id": 1, "balance": 100.0})

    with db.transaction():
        db.sql.update("accounts", {"balance": 50.0}, {"id": 1})

    result = db.sql.select("accounts", where={"id": 1})
    assert result.rows[0]["balance"] == 50.0


def test_transaction_rollback(db):
    schema = TableSchema(
        name="accounts",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="balance", col_type=ColumnType.REAL),
        ],
    )
    db.sql.create_table(schema)
    db.sql.insert("accounts", {"id": 1, "balance": 100.0})

    try:
        with db.transaction():
            db.sql.update("accounts", {"balance": 0.0}, {"id": 1})
            raise ValueError("Simulated error")
    except ValueError:
        pass

    result = db.sql.select("accounts", where={"id": 1})
    assert result.rows[0]["balance"] == 100.0


def test_database_repr(db):
    assert "Database(path=" in repr(db)
