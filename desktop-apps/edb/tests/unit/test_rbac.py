"""Unit tests for RBAC."""

import pytest

from edb.auth.models import Permission, Role
from edb.auth.rbac import PermissionDeniedError, RBACManager


def test_admin_has_all_permissions():
    rbac = RBACManager()
    for perm in Permission:
        assert rbac.has_permission(Role.ADMIN, perm)


def test_read_only_permissions():
    rbac = RBACManager()
    assert rbac.has_permission(Role.READ_ONLY, Permission.DB_READ)
    assert rbac.has_permission(Role.READ_ONLY, Permission.EBOT_QUERY)
    assert not rbac.has_permission(Role.READ_ONLY, Permission.DB_WRITE)
    assert not rbac.has_permission(Role.READ_ONLY, Permission.DB_DELETE)
    assert not rbac.has_permission(Role.READ_ONLY, Permission.ADMIN_USERS)


def test_read_write_permissions():
    rbac = RBACManager()
    assert rbac.has_permission(Role.READ_WRITE, Permission.DB_READ)
    assert rbac.has_permission(Role.READ_WRITE, Permission.DB_WRITE)
    assert rbac.has_permission(Role.READ_WRITE, Permission.DB_DELETE)
    assert not rbac.has_permission(Role.READ_WRITE, Permission.ADMIN_USERS)


def test_check_permission_raises():
    rbac = RBACManager()
    with pytest.raises(PermissionDeniedError):
        rbac.check_permission(Role.READ_ONLY, Permission.DB_WRITE)


def test_string_role():
    rbac = RBACManager()
    assert rbac.has_permission("admin", Permission.DB_READ)
    assert rbac.has_permission("read_only", Permission.DB_READ)
    assert not rbac.has_permission("read_only", Permission.DB_WRITE)


def test_custom_role():
    rbac = RBACManager()
    rbac.create_custom_role("analyst", {Permission.DB_READ, Permission.EBOT_QUERY})

    assert rbac.has_permission("analyst", Permission.DB_READ)
    assert rbac.has_permission("analyst", Permission.EBOT_QUERY)
    assert not rbac.has_permission("analyst", Permission.DB_WRITE)


def test_convenience_methods():
    rbac = RBACManager()
    assert rbac.can_read(Role.READ_ONLY)
    assert not rbac.can_write(Role.READ_ONLY)
    assert rbac.is_admin(Role.ADMIN)
    assert not rbac.is_admin(Role.READ_WRITE)
