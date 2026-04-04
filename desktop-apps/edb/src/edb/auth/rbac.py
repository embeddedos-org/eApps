"""Role-Based Access Control (RBAC) for eDB.

Enforces permission checks based on user roles.
"""

from __future__ import annotations

from edb.auth.models import ROLE_PERMISSIONS, Permission, Role


class RBACManager:
    """Manages role-based access control."""

    def __init__(self) -> None:
        self._role_permissions: dict[Role, set[Permission]] = dict(ROLE_PERMISSIONS)
        self._custom_roles: dict[str, set[Permission]] = {}

    def has_permission(self, role: Role | str, permission: Permission) -> bool:
        """Check if a role has a specific permission."""
        if isinstance(role, str):
            try:
                role = Role(role)
            except ValueError:
                return permission in self._custom_roles.get(role, set())

        return permission in self._role_permissions.get(role, set())

    def check_permission(self, role: Role | str, permission: Permission) -> None:
        """Check permission and raise if denied."""
        if not self.has_permission(role, permission):
            raise PermissionDeniedError(
                f"Role '{role}' does not have permission '{permission.value}'"
            )

    def get_permissions(self, role: Role | str) -> set[Permission]:
        """Get all permissions for a role."""
        if isinstance(role, str):
            try:
                role = Role(role)
            except ValueError:
                return self._custom_roles.get(role, set())
        return self._role_permissions.get(role, set())

    def create_custom_role(self, name: str, permissions: set[Permission]) -> None:
        """Create a custom role with specific permissions."""
        self._custom_roles[name] = permissions

    def can_read(self, role: Role | str) -> bool:
        return self.has_permission(role, Permission.DB_READ)

    def can_write(self, role: Role | str) -> bool:
        return self.has_permission(role, Permission.DB_WRITE)

    def can_delete(self, role: Role | str) -> bool:
        return self.has_permission(role, Permission.DB_DELETE)

    def is_admin(self, role: Role | str) -> bool:
        return self.has_permission(role, Permission.ADMIN_USERS)


class PermissionDeniedError(Exception):
    """Raised when a user lacks the required permission."""
