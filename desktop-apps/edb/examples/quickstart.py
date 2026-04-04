"""eDB Quickstart Example — demonstrates all three data models."""

from edb.core.database import Database
from edb.core.models import ColumnDefinition, ColumnType, TableSchema


def main():
    # Create an in-memory database
    db = Database(":memory:")

    print("=== eDB Quickstart ===\n")

    # --- 1. Relational (SQL) ---
    print("--- SQL Store ---")
    schema = TableSchema(
        name="employees",
        columns=[
            ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
            ColumnDefinition(name="name", col_type=ColumnType.TEXT, nullable=False),
            ColumnDefinition(name="department", col_type=ColumnType.TEXT),
            ColumnDefinition(name="salary", col_type=ColumnType.REAL),
        ],
    )
    db.sql.create_table(schema)

    db.sql.insert(
        "employees",
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": 95000},
    )
    db.sql.insert("employees", {"id": 2, "name": "Bob", "department": "Marketing", "salary": 75000})
    db.sql.insert(
        "employees",
        {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 105000},
    )

    result = db.sql.select("employees", where={"department": "Engineering"})
    print(f"Engineers: {[r['name'] for r in result.rows]}")

    db.sql.update("employees", {"salary": 100000}, {"name": "Alice"})
    result = db.sql.select("employees", where={"name": "Alice"})
    print(f"Alice's new salary: {result.rows[0]['salary']}")

    # --- 2. Document Store (NoSQL) ---
    print("\n--- Document Store ---")
    db.docs.insert("projects", {
        "name": "eDB",
        "status": "active",
        "team": ["Alice", "Charlie"],
        "budget": 500000,
    })
    db.docs.insert("projects", {
        "name": "Marketing Campaign",
        "status": "planning",
        "team": ["Bob"],
        "budget": 100000,
    })

    active = db.docs.find("projects", filter_dict={"status": "active"})
    print(f"Active projects: {[d.data['name'] for d in active]}")
    print(f"Total projects: {db.docs.count('projects')}")

    # --- 3. Key-Value Store ---
    print("\n--- Key-Value Store ---")
    db.kv.set("config:app_name", "eDB Demo")
    db.kv.set("config:version", "0.1.0")
    db.kv.set("cache:user:1", {"name": "Alice", "role": "admin"}, ttl=3600)

    print(f"App: {db.kv.get('config:app_name')}")
    print(f"Config keys: {db.kv.list_keys(prefix='config:')}")
    print(f"Cached user: {db.kv.get('cache:user:1')}")

    # --- 4. Cross-model Transaction ---
    print("\n--- Transaction ---")
    try:
        with db.transaction():
            db.sql.insert(
                "employees",
                {"id": 4, "name": "Diana", "department": "Sales", "salary": 80000},
            )
            db.docs.insert(
                "projects",
                {"name": "Sales Push", "status": "active", "team": ["Diana"]},
            )
            db.kv.set("cache:user:4", {"name": "Diana"})
        print("Transaction committed successfully")
    except Exception as e:
        print(f"Transaction rolled back: {e}")

    result = db.sql.select("employees")
    print(f"Total employees: {result.row_count}")

    db.close()
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
