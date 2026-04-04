# eDB API Reference

Base URL: `http://localhost:8000`

All endpoints except `/auth/register`, `/auth/login`, and `/health` require a `Bearer` token in the `Authorization` header.

---

## Health

### `GET /health`
Returns server health status.

**Response:** `{"status": "healthy", "version": "0.1.0"}`

---

## Authentication

### `POST /auth/register`
Register a new user.

**Body:**
```json
{"username": "alice", "password": "secure123", "role": "read_only"}
```

### `POST /auth/login`
Authenticate and receive tokens.

**Body:** `{"username": "alice", "password": "secure123"}`

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### `POST /auth/refresh`
Refresh an access token.

**Body:** `{"refresh_token": "eyJ..."}`

### `GET /auth/me`
Get current user profile. Requires auth.

---

## SQL (Relational)

### `POST /sql/tables`
Create a table.

**Body:**
```json
{
  "name": "users",
  "columns": [
    {"name": "id", "col_type": "INTEGER", "primary_key": true},
    {"name": "name", "col_type": "TEXT", "nullable": false},
    {"name": "email", "col_type": "TEXT", "unique": true}
  ]
}
```

### `GET /sql/tables`
List all tables.

### `GET /sql/tables/{table_name}?limit=100&offset=0`
Get table data.

### `POST /sql/tables/{table_name}/select`
Query with filters.

**Body:**
```json
{
  "columns": ["name", "email"],
  "where": {"name": "Alice"},
  "order_by": "name ASC",
  "limit": 10
}
```

### `POST /sql/tables/{table_name}/insert`
Insert a row.

**Body:** `{"data": {"name": "Alice", "email": "alice@test.com"}}`

### `PUT /sql/tables/{table_name}/update`
Update rows.

**Body:** `{"data": {"email": "newemail@test.com"}, "where": {"name": "Alice"}}`

### `DELETE /sql/tables/{table_name}/delete`
Delete rows.

**Body:** `{"where": {"name": "Alice"}}`

### `POST /sql/execute`
Execute raw SQL (requires `db:write` permission).

**Body:** `{"sql": "SELECT COUNT(*) FROM users", "params": []}`

---

## Documents (NoSQL)

### `GET /docs/collections`
List all collections.

### `POST /docs/{collection}`
Insert a document.

**Body:** `{"data": {"name": "Alice", "age": 30}, "doc_id": "optional-custom-id"}`

### `POST /docs/{collection}/find`
Find documents.

**Body:** `{"filter": {"name": "Alice"}, "limit": 10, "offset": 0}`

### `GET /docs/{collection}/{doc_id}`
Get document by ID.

### `PUT /docs/{collection}/{doc_id}`
Update document.

**Body:** `{"data": {"age": 31}, "merge": true}`

### `DELETE /docs/{collection}/{doc_id}`
Delete document.

---

## Key-Value

### `GET /kv/keys?prefix=user:`
List keys.

### `GET /kv/{key}`
Get value.

### `PUT /kv/{key}`
Set value.

**Body:** `{"value": {"theme": "dark"}, "ttl": 3600}`

### `DELETE /kv/{key}`
Delete key.

---

## ebot (AI)

### `POST /ebot/query`
Natural language query.

**Body:**
```json
{"text": "show all users", "execute": true}
```

**Response:**
```json
{
  "success": true,
  "original_text": "show all users",
  "translated_query": {"type": "sql", "action": "select", "table": "users"},
  "confidence": 0.7,
  "explanation": "SELECT all from 'users'",
  "result": {"success": true, "data": [...], "row_count": 5}
}
```

---

## Admin

### `GET /admin/users`
List all users (admin only).

### `PUT /admin/users/{user_id}/role`
Update user role.

**Body:** `{"role": "read_write"}`

### `DELETE /admin/users/{user_id}`
Deactivate a user.

### `GET /admin/audit?event_type=auth&limit=100`
Get audit logs.

### `GET /admin/audit/verify`
Verify audit log hash chain integrity.

### `GET /admin/stats`
Get database statistics.
