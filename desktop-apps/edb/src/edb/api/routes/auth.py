"""Authentication API routes for eDB."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from edb.api.dependencies import AppState, get_app_state, get_current_user
from edb.auth.models import (
    LoginRequest,
    TokenPair,
    UserCreate,
    UserResponse,
)

router = APIRouter()




@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    state: Annotated[AppState, Depends(get_app_state)],
) -> UserResponse:
    """Register a new user."""
    try:
        user = state.user_manager.create_user(user_data)
        state.audit.log(
            event_type="auth",
            action="user_registered",
            user_id=user.id,
            username=user.username,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.post("/login", response_model=TokenPair)
def login(
    credentials: LoginRequest,
    state: Annotated[AppState, Depends(get_app_state)],
) -> TokenPair:
    """Authenticate and get access/refresh tokens."""
    user = state.user_manager.authenticate(credentials.username, credentials.password)
    if user is None:
        state.audit.log(
            event_type="auth",
            action="login_failed",
            details={"username": credentials.username},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    tokens = state.jwt_handler.create_token_pair(user.id, user.username, user.role.value)
    state.audit.log(
        event_type="auth",
        action="login_success",
        user_id=user.id,
        username=user.username,
    )
    return TokenPair(**tokens)


@router.post("/refresh", response_model=TokenPair)
def refresh_token(
    refresh_token: dict[str, str],
    state: Annotated[AppState, Depends(get_app_state)],
) -> TokenPair:
    """Refresh access token using a refresh token."""
    token = refresh_token.get("refresh_token", "")
    payload = state.jwt_handler.verify_token(token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = state.user_manager.get_by_id(payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    tokens = state.jwt_handler.create_token_pair(user.id, user.username, user.role.value)
    return TokenPair(**tokens)


@router.get("/me", response_model=UserResponse)
def get_me(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    state: Annotated[AppState, Depends(get_app_state)],
) -> UserResponse:
    """Get current authenticated user's profile."""
    db_user = state.user_manager.get_by_id(user["sub"])
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        role=db_user.role,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
    )


@router.post("/password")
def change_password(
    body: dict[str, str],
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    state: Annotated[AppState, Depends(get_app_state)],
):
    """Change the current user's password."""
    result = state.user_manager.change_password(
        user["sub"], body["current_password"], body["new_password"]
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong current password",
        )
    return {"message": "Password changed successfully"}


@router.post("/logout")
def logout(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
):
    """Log out the current user (client should discard tokens)."""
    return {"message": "Logged out successfully"}
