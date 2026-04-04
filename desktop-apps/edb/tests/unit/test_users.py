"""Unit tests for UserManager."""

import pytest

from edb.auth.models import Role, UserCreate
from edb.auth.users import UserManager


def test_create_user(engine):
    mgr = UserManager(engine)
    user = mgr.create_user(
        UserCreate(username="alice", password="password123", role=Role.READ_WRITE)
    )
    assert user.username == "alice"
    assert user.role == Role.READ_WRITE
    assert user.is_active is True


def test_create_duplicate_user(engine):
    mgr = UserManager(engine)
    mgr.create_user(UserCreate(username="alice", password="password123"))
    with pytest.raises(ValueError, match="already exists"):
        mgr.create_user(UserCreate(username="alice", password="other_pass"))


def test_authenticate_success(engine):
    mgr = UserManager(engine)
    mgr.create_user(UserCreate(username="alice", password="password123"))
    user = mgr.authenticate("alice", "password123")
    assert user is not None
    assert user.username == "alice"


def test_authenticate_wrong_password(engine):
    mgr = UserManager(engine)
    mgr.create_user(UserCreate(username="alice", password="password123"))
    user = mgr.authenticate("alice", "wrongpass")
    assert user is None


def test_authenticate_nonexistent(engine):
    mgr = UserManager(engine)
    user = mgr.authenticate("ghost", "password123")
    assert user is None


def test_change_password(engine):
    mgr = UserManager(engine)
    created = mgr.create_user(UserCreate(username="alice", password="password123"))
    success = mgr.change_password(created.id, "password123", "newpassword123")
    assert success is True
    assert mgr.authenticate("alice", "newpassword123") is not None
    assert mgr.authenticate("alice", "password123") is None


def test_change_password_wrong_current(engine):
    mgr = UserManager(engine)
    created = mgr.create_user(UserCreate(username="alice", password="password123"))
    success = mgr.change_password(created.id, "wrongcurrent", "newpassword123")
    assert success is False


def test_get_by_id(engine):
    mgr = UserManager(engine)
    created = mgr.create_user(UserCreate(username="alice", password="password123"))
    user = mgr.get_by_id(created.id)
    assert user is not None
    assert user.username == "alice"


def test_get_by_username(engine):
    mgr = UserManager(engine)
    mgr.create_user(UserCreate(username="alice", password="password123"))
    user = mgr.get_by_username("alice")
    assert user is not None


def test_list_users(engine):
    mgr = UserManager(engine)
    mgr.create_user(UserCreate(username="alice", password="password123"))
    mgr.create_user(UserCreate(username="bob", password="password456"))
    users = mgr.list_users()
    assert len(users) == 2


def test_update_role(engine):
    mgr = UserManager(engine)
    created = mgr.create_user(UserCreate(username="alice", password="password123"))
    success = mgr.update_role(created.id, Role.ADMIN)
    assert success is True
    user = mgr.get_by_id(created.id)
    assert user.role == Role.ADMIN


def test_deactivate_user(engine):
    mgr = UserManager(engine)
    created = mgr.create_user(UserCreate(username="alice", password="password123"))
    success = mgr.deactivate_user(created.id)
    assert success is True
    assert mgr.authenticate("alice", "password123") is None


def test_ensure_admin_exists(engine):
    mgr = UserManager(engine)
    mgr.ensure_admin_exists()
    admin = mgr.get_by_username("admin")
    assert admin is not None
    assert admin.role == Role.ADMIN
    mgr.ensure_admin_exists()  # idempotent
    users = mgr.list_users()
    assert sum(1 for u in users if u.username == "admin") == 1
