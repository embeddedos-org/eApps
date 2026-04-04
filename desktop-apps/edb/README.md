# eDB: Unified Multi-Model Database Ecosystem

[![CI](https://github.com/your-org/edb/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/edb/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**eDB** is a unified multi-model database that combines **SQL**, **Document/NoSQL**, and **Key-Value** storage in a single embedded engine. Built on SQLite with zero external dependencies, it provides a REST API, JWT authentication, RBAC, encryption at rest, and an AI-powered natural language query interface.

## Features

| Feature | Description |
|---------|-------------|
| 🗃️ **Multi-Model Storage** | SQL tables, JSON documents, and key-value pairs — all in one database |
| 🔐 **JWT Authentication** | Access and refresh tokens with configurable expiration |
| 👥 **RBAC** | Admin, read_write, read_only roles with granular permissions |
| 🔒 **AES-256 Encryption** | Field-level encryption at rest using AES-256-GCM |
| 📋 **Audit Logging** | Tamper-resistant logs with hash chain verification |
| 🤖 **ebot AI** | Natural language → SQL/NoSQL translation |
| 🌐 **REST API** | Full CRUD via FastAPI with auto-generated OpenAPI docs |
| 🛡️ **Input Sanitization** | SQL injection, NoSQL injection, and prompt injection detection |
| ⚡ **Zero Dependencies** | Core engine runs on SQLite — no external database needed |
| 📦 **Embeddable** | Use as a Python library or standalone server |

## Quick Start

### Install

```bash
git clone https://github.com/your-org/edb.git
cd edb
pip install -e ".[dev]"
```

### As a Python Library

```python
from edb.core.database import Database
from edb.core.models import ColumnDefinition, ColumnType, TableSchema

db = Database("my_app.db")

# SQL
schema = TableSchema(name="users", columns=[
    ColumnDefinition(name="id", col_type=ColumnType.INTEGER, primary_key=True),
    ColumnDefinition(name="name", col_type=ColumnType.TEXT),
])
db.sql.create_table(schema)
db.sql.insert("users", {"id": 1, "name": "Alice"})

# Documents
db.docs.insert("logs", {"event": "login", "user": "Alice"})

# Key-Value
db.kv.set("session:abc", {"user_id": 1}, ttl=3600)
```

### As an API Server

```bash
# Initialize database with default admin
edb init

# Start the server
edb serve --port 8000

# API docs at http://localhost:8000/docs
```

### Interactive Shell

```bash
edb shell
# edb> SELECT * FROM users
# edb> .tables
# edb> .collections
```

## Architecture

```
eDB
├── Core Engine (SQLite)
│   ├── Relational Store (SQL)
│   ├── Document Store (JSON/NoSQL)
│   └── Key-Value Store (with TTL)
├── Query Layer
│   ├── JSON Query DSL Parser
│   └── Query Planner & Router
├── Security
│   ├── JWT Authentication
│   ├── RBAC (Role-Based Access Control)
│   ├── AES-256 Encryption at Rest
│   ├── Audit Logging (hash chain)
│   └── Input Sanitization
├── API Layer (FastAPI)
│   ├── SQL Endpoints
│   ├── Document Endpoints
│   ├── Key-Value Endpoints
│   ├── Auth Endpoints
│   ├── Admin Endpoints
│   └── ebot AI Endpoint
└── ebot (AI/NLP)
    ├── Rule-based Translator
    └── Prompt Sanitizer
```

See [docs/architecture.md](docs/architecture.md) for detailed diagrams.

## Configuration

Configure via environment variables (prefix `EDB_`) or `.env` file:

```bash
EDB_DB_PATH=my_data.db
EDB_API_HOST=0.0.0.0
EDB_API_PORT=8000
EDB_JWT_SECRET=your-strong-secret-here
EDB_ENCRYPTION_KEY=your-encryption-key
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/
```

## Project Structure

```
eDB/
├── src/edb/
│   ├── core/          # Storage engines (engine, relational, document, keyvalue)
│   ├── query/         # Query parser and planner
│   ├── auth/          # JWT, users, RBAC
│   ├── security/      # Encryption, audit, input validation
│   ├── api/           # FastAPI routes and dependencies
│   ├── ebot/          # AI/NLP query interface
│   ├── config.py      # Pydantic Settings configuration
│   └── cli.py         # CLI entry point
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── docs/              # Documentation
├── examples/          # Runnable examples
└── pyproject.toml     # Project metadata
```

## Roadmap

- [x] Core multi-model engine (SQL, Document, KV)
- [x] Query DSL with parser and planner
- [x] JWT authentication and RBAC
- [x] AES-256 encryption at rest
- [x] Tamper-resistant audit logging
- [x] REST API (FastAPI)
- [x] ebot rule-based NL queries
- [x] CLI (serve, init, shell)
- [x] CI/CD pipeline
- [ ] LLM-powered ebot (OpenAI/local models)
- [ ] Graph data model (Neo4j-style)
- [ ] Multi-node clustering (eDBE)
- [ ] GraphQL and gRPC interfaces
- [ ] File/blob storage with indexing
- [ ] Predictive analytics integration

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and security best practices.

## License

MIT License. See [LICENSE](LICENSE) for details.
