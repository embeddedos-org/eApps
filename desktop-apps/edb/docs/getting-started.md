# Getting Started with eDB

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/edb.git
cd edb

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start: Python Library

```python
from edb.core.database import Database
from edb.core.models import ColumnDefinition, ColumnType, TableSchema

# Create a database (in-memory or file-backed)
db = Database("my_app.db")

# --- SQL (Relational) ---
schema = TableSchema(
    name="users",
    columns=[
        ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
        ColumnDefinition(name="name", col_type=ColumnType.TEXT, nullable=False),
        ColumnDefinition(name="email", col_type=ColumnType.TEXT, unique=True),
    ],
)
db.sql.create_table(schema)
db.sql.insert("users", {"id": 1, "name": "Alice", "email": "alice@example.com"})

result = db.sql.select("users", where={"name": "Alice"})
print(result.rows)  # [{"id": 1, "name": "Alice", "email": "alice@example.com"}]

# --- Document Store (NoSQL) ---
doc = db.docs.insert("logs", {"event": "user_created", "user_id": 1, "level": "info"})
print(doc.id)  # UUID

logs = db.docs.find("logs", filter_dict={"level": "info"})
print(len(logs))  # 1

# --- Key-Value Store ---
db.kv.set("session:abc123", {"user_id": 1, "role": "admin"}, ttl=3600)
session = db.kv.get("session:abc123")
print(session)  # {"user_id": 1, "role": "admin"}

# --- Transactions ---
with db.transaction():
    db.sql.insert("users", {"id": 2, "name": "Bob", "email": "bob@example.com"})
    db.docs.insert("logs", {"event": "user_created", "user_id": 2})
    # If any operation fails, everything rolls back

db.close()
```

## Quick Start: CLI

```bash
# Initialize a new database with default admin user
edb init --db my_app.db

# Open interactive SQL shell
edb shell --db my_app.db
# edb> CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)
# edb> INSERT INTO products VALUES (1, 'Widget', 9.99)
# edb> SELECT * FROM products
# edb> .tables
# edb> .collections
# edb> exit

# Start the API server
edb serve --host 0.0.0.0 --port 8000 --db my_app.db
```

## Quick Start: REST API

```bash
# Start the server
edb serve

# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secure123", "role": "read_write"}'

# Login and get tokens
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin1234"}'

# Use the access_token from login response
TOKEN="<your-access-token>"

# Create a table
curl -X POST http://localhost:8000/sql/tables \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "products", "columns": [{"name": "id", "col_type": "INTEGER", "primary_key": true}, {"name": "name", "col_type": "TEXT"}]}'

# Insert data
curl -X POST http://localhost:8000/sql/tables/products/insert \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"id": 1, "name": "Widget"}}'

# Natural language query via ebot
curl -X POST http://localhost:8000/ebot/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "show all products"}'
```

## Configuration

eDB is configured via environment variables (prefixed with `EDB_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `EDB_DB_PATH` | `edb_data.db` | Database file path |
| `EDB_API_HOST` | `127.0.0.1` | API server host |
| `EDB_API_PORT` | `8000` | API server port |
| `EDB_JWT_SECRET` | (default) | JWT signing secret — **change in production!** |
| `EDB_ENCRYPTION_KEY` | (default) | AES-256 encryption key — **change in production!** |
| `EDB_EBOT_ENABLED` | `true` | Enable ebot AI queries |
| `EDB_AUDIT_ENABLED` | `true` | Enable audit logging |

You can also use a `.env` file in the project root.

## Running Tests

```bash
pytest                          # Run all tests
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest --cov=edb --cov-report=html  # With coverage report
```
