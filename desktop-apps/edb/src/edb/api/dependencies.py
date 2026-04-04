"""FastAPI dependency injection for eDB."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from edb.auth.jwt_handler import JWTHandler
from edb.auth.models import Permission
from edb.auth.rbac import RBACManager
from edb.auth.users import UserManager
from edb.config import EDBConfig
from edb.core.database import Database
from edb.security.audit import AuditLogger
from edb.security.encryption import EncryptionManager
from edb.security.input_validation import InputValidator

logger = logging.getLogger("edb.api")
security_scheme = HTTPBearer(auto_error=False)




class AppState:
    """Shared application state holding all service instances."""

    def __init__(self, config: EDBConfig | None = None) -> None:
        self.config = config or EDBConfig()
        self.database = Database(self.config.db_path)
        self.jwt_handler = JWTHandler(
            secret_key=self.config.jwt_secret,
            access_token_expire_minutes=self.config.jwt_access_expire_minutes,
            refresh_token_expire_days=self.config.jwt_refresh_expire_days,
        )
        self.user_manager = UserManager(self.database.engine)
        self.rbac = RBACManager()
        self.audit = AuditLogger(self.database.engine)
        self.encryption = EncryptionManager(self.config.encryption_key)
        self.validator = InputValidator()


def get_app_state(request: Request) -> AppState:
    """Get the shared AppState from the request."""
    return request.app.state.edb


def get_database(state: Annotated[AppState, Depends(get_app_state)]) -> Database:
    return state.database


def get_jwt_handler(state: Annotated[AppState, Depends(get_app_state)]) -> JWTHandler:
    return state.jwt_handler


def get_user_manager(state: Annotated[AppState, Depends(get_app_state)]) -> UserManager:
    return state.user_manager


def get_audit(state: Annotated[AppState, Depends(get_app_state)]) -> AuditLogger:
    return state.audit


async def get_current_user(
    state: Annotated[AppState, Depends(get_app_state)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)] = None,
) -> dict[str, Any]:
    """Extract and verify the current user from JWT token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = state.jwt_handler.verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return payload


def require_permission(permission: Permission):
    """Create a dependency that checks for a specific permission."""

    async def check(
        state: Annotated[AppState, Depends(get_app_state)],
        user: Annotated[dict[str, Any], Depends(get_current_user)],
    ) -> dict[str, Any]:
        role = user.get("role", "")
        if not state.rbac.has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}",
            )
        return user

    return check


def require_admin():
    """Dependency that requires admin role."""
    return require_permission(Permission.ADMIN_USERS)
