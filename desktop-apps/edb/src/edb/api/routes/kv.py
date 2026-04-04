"""Key-Value store API routes for eDB."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from edb.api.dependencies import (
    AppState,
    get_app_state,
    require_permission,
)
from edb.auth.models import Permission

router = APIRouter()


class KVSetRequest(BaseModel):
    value: Any
    ttl: int | None = None


@router.get("/keys")
def list_keys(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
    prefix: str | None = None,
) -> dict[str, list[str]]:
    """List all keys, optionally filtered by prefix."""
    keys = state.database.kv.list_keys(prefix)
    return {"keys": keys}


@router.get("/{key:path}")
def get_value(
    key: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, Any]:
    """Get a value by key."""
    value = state.database.kv.get(key)
    if value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    return {"key": key, "value": value}


@router.put("/{key:path}")
def set_value(
    key: str,
    request: KVSetRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    """Set a key-value pair."""
    entry = state.database.kv.set(key, request.value, request.ttl)
    state.audit.log(
        event_type="query",
        action="kv_set",
        user_id=user.get("sub"),
        details={"key": key},
    )
    return entry.model_dump(mode="json")


@router.delete("/{key:path}")
def delete_key(
    key: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_DELETE))],
) -> dict[str, bool]:
    """Delete a key."""
    deleted = state.database.kv.delete(key)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Key not found")
    state.audit.log(
        event_type="query",
        action="kv_delete",
        user_id=user.get("sub"),
        details={"key": key},
    )
    return {"deleted": True}
