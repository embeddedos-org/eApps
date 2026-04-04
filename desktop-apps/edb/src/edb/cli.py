"""eDB CLI entry point.

Provides commands: serve, init, shell, backup, restore, version
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="edb", description="eDB: Unified Multi-Model Database")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    serve_p = subparsers.add_parser("serve", help="Start the eDB API server")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8000)
    serve_p.add_argument("--reload", action="store_true")
    serve_p.add_argument("--db", default="edb_data.db")

    init_p = subparsers.add_parser("init", help="Initialize a new eDB database")
    init_p.add_argument("--db", default="edb_data.db")

    shell_p = subparsers.add_parser("shell", help="Open interactive SQL shell")
    shell_p.add_argument("--db", default="edb_data.db")

    backup_p = subparsers.add_parser("backup", help="Backup the database")
    backup_p.add_argument("--db", default="edb_data.db")
    backup_p.add_argument("--dest", required=True, help="Backup destination path")

    restore_p = subparsers.add_parser("restore", help="Restore database from backup")
    restore_p.add_argument("--source", required=True, help="Backup file to restore from")
    restore_p.add_argument("--db", default="edb_data.db", help="Target database path")

    subparsers.add_parser("version", help="Show eDB version")

    args = parser.parse_args()

    if args.command == "serve":
        _cmd_serve(args)
    elif args.command == "init":
        _cmd_init(args)
    elif args.command == "shell":
        _cmd_shell(args)
    elif args.command == "backup":
        _cmd_backup(args)
    elif args.command == "restore":
        _cmd_restore(args)
    elif args.command == "version":
        _cmd_version()
    else:
        parser.print_help()


def _cmd_serve(args: argparse.Namespace) -> None:
    import os
    os.environ.setdefault("EDB_DB_PATH", args.db)
    os.environ.setdefault("EDB_API_HOST", args.host)
    os.environ.setdefault("EDB_API_PORT", str(args.port))

    import uvicorn
    print(f"🚀 Starting eDB API server on {args.host}:{args.port}")
    print(f"📁 Database: {args.db}")
    print(f"📖 API docs: http://{args.host}:{args.port}/docs")
    uvicorn.run(
        "edb.api.app:create_app",
        host=args.host, port=args.port,
        reload=args.reload, factory=True,
    )


def _cmd_init(args: argparse.Namespace) -> None:
    from edb.auth.users import UserManager
    from edb.core.database import Database
    from edb.security.audit import AuditLogger

    print(f"📦 Initializing eDB database at: {args.db}")
    db = Database(args.db)
    UserManager(db.engine).ensure_admin_exists()
    AuditLogger(db.engine)
    db.close()
    print("✅ Database initialized successfully")
    print("   Default admin: admin / admin1234")
    print("   ⚠️  Change the admin password before production use!")


def _cmd_shell(args: argparse.Namespace) -> None:
    from edb.core.database import Database

    db = Database(args.db)
    print(f"🔗 Connected to: {args.db}")
    print("   Type SQL or 'exit'. Use '.tables', '.collections', '.graph'")
    print()

    try:
        while True:
            try:
                query = input("edb> ").strip()
            except EOFError:
                break

            if not query:
                continue
            if query.lower() in ("exit", "quit", "\\q"):
                break
            if query == ".tables":
                for t in db.sql.list_tables():
                    print(f"  {t}")
                continue
            if query == ".collections":
                for c in db.docs.list_collections():
                    print(f"  {c}")
                continue
            if query == ".graph":
                print(f"  Nodes: {db.graph.node_count()}, Edges: {db.graph.edge_count()}")
                continue

            try:
                result = db.sql.execute_raw(query)
                if result.rows:
                    if result.columns:
                        print("  " + " | ".join(result.columns))
                        print("  " + "-+-".join("-" * max(len(c), 8) for c in result.columns))
                    for row in result.rows:
                        print("  " + " | ".join(str(v) for v in row.values()))
                    print(f"  ({result.row_count} rows)")
                else:
                    print(f"  OK (affected: {result.affected_rows})")
            except Exception as e:
                print(f"  Error: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        print("\n👋 Bye!")


def _cmd_backup(args: argparse.Namespace) -> None:
    from edb.core.database import Database
    db = Database(args.db)
    db.engine.backup(args.dest)
    db.close()
    print(f"✅ Backup created: {args.dest}")


def _cmd_restore(args: argparse.Namespace) -> None:
    import shutil
    shutil.copy2(args.source, args.db)
    print(f"✅ Database restored from {args.source} to {args.db}")


def _cmd_version() -> None:
    from edb import __version__
    print(f"eDB v{__version__}")


if __name__ == "__main__":
    main()
