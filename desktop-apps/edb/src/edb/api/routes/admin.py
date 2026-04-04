"""Admin API routes for eDB."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from edb.api.dependencies import (
    AppState,
    get_app_state,
    require_permission,
)
from edb.auth.models import Permission, Role, UserResponse

router = APIRouter()


class UpdateRoleRequest(BaseModel):
    role: Role


@router.get("/users", response_model=list[UserResponse])
def list_users(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.ADMIN_USERS))],
) -> list[UserResponse]:
    """List all users (admin only)."""
    return state.user_manager.list_users()


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    request: UpdateRoleRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.ADMIN_ROLES))],
) -> dict[str, str]:
    """Update a user's role (admin only)."""
    success = state.user_manager.update_role(user_id, request.role)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    state.audit.log(
        event_type="admin",
        action="role_updated",
        user_id=user.get("sub"),
        details={"target_user": user_id, "new_role": request.role.value},
    )
    return {"message": f"Role updated to {request.role.value}"}


@router.delete("/users/{user_id}")
def deactivate_user(
    user_id: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.ADMIN_USERS))],
) -> dict[str, str]:
    """Deactivate a user account (admin only)."""
    if user_id == user.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself"
        )
    success = state.user_manager.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    state.audit.log(
        event_type="admin",
        action="user_deactivated",
        user_id=user.get("sub"),
        details={"target_user": user_id},
    )
    return {"message": "User deactivated"}


@router.get("/audit")
def get_audit_logs(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.ADMIN_AUDIT))],
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Get audit log entries (admin only)."""
    logs = state.audit.get_logs(event_type=event_type, limit=limit, offset=offset)
    return {"logs": logs, "count": len(logs)}


@router.get("/audit/verify")
def verify_audit_chain(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.ADMIN_AUDIT))],
) -> dict[str, Any]:
    """Verify audit log hash chain integrity (admin only)."""
    is_valid, message = state.audit.verify_chain()
    return {"valid": is_valid, "message": message}


@router.get("/stats")
def get_stats(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.ADMIN_USERS))],
) -> dict[str, Any]:
    """Get database statistics (admin only)."""
    return {
        "tables": state.database.sql.list_tables(),
        "collections": state.database.docs.list_collections(),
        "kv_count": state.database.kv.count(),
        "audit_entries": state.audit.count(),
        "users": len(state.user_manager.list_users()),
    }
