"""Unit tests for audit logging."""

from edb.security.audit import AuditLogger


def test_log_event(engine):
    audit = AuditLogger(engine)
    entry_id = audit.log(
        event_type="auth",
        action="login_success",
        user_id="user-1",
        username="alice",
    )
    assert entry_id > 0


def test_get_logs(engine):
    audit = AuditLogger(engine)
    audit.log(event_type="auth", action="login", user_id="user-1")
    audit.log(event_type="query", action="select", user_id="user-1")
    audit.log(event_type="auth", action="logout", user_id="user-1")

    all_logs = audit.get_logs()
    assert len(all_logs) == 3

    auth_logs = audit.get_logs(event_type="auth")
    assert len(auth_logs) == 2

    user_logs = audit.get_logs(user_id="user-1")
    assert len(user_logs) == 3


def test_verify_chain_valid(engine):
    audit = AuditLogger(engine)
    audit.log(event_type="auth", action="login")
    audit.log(event_type="query", action="select")
    audit.log(event_type="auth", action="logout")

    is_valid, message = audit.verify_chain()
    assert is_valid
    assert "3 entries intact" in message


def test_verify_chain_empty(engine):
    audit = AuditLogger(engine)
    is_valid, message = audit.verify_chain()
    assert is_valid
    assert "empty" in message


def test_log_with_details(engine):
    audit = AuditLogger(engine)
    audit.log(
        event_type="query",
        action="sql_execute",
        user_id="user-1",
        details={"sql": "SELECT * FROM users", "rows_returned": 10},
    )

    logs = audit.get_logs()
    assert logs[0]["details"]["sql"] == "SELECT * FROM users"
    assert logs[0]["details"]["rows_returned"] == 10


def test_count(engine):
    audit = AuditLogger(engine)
    assert audit.count() == 0

    audit.log(event_type="test", action="a")
    audit.log(event_type="test", action="b")
    assert audit.count() == 2
