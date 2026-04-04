"""Pydantic models for eDB authentication and authorization."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    ADMIN = "admin"
    READ_WRITE = "read_write"
    READ_ONLY = "read_only"


class Permission(StrEnum):
    DB_READ = "db:read"
    DB_WRITE = "db:write"
    DB_DELETE = "db:delete"
    DB_CREATE_TABLE = "db:create_table"
    DB_DROP_TABLE = "db:drop_table"
    ADMIN_USERS = "admin:users"
    ADMIN_ROLES = "admin:roles"
    ADMIN_AUDIT = "admin:audit"
    EBOT_QUERY = "ebot:query"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.READ_WRITE: {
        Permission.DB_READ, Permission.DB_WRITE, Permission.DB_DELETE,
        Permission.DB_CREATE_TABLE, Permission.EBOT_QUERY,
    },
    Role.READ_ONLY: {Permission.DB_READ, Permission.EBOT_QUERY},
}


class User(BaseModel):
    id: str
    username: str
    password_hash: str
    role: Role = Role.READ_ONLY
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    role: Role = Role.READ_ONLY


class UserResponse(BaseModel):
    id: str
    username: str
    role: Role
    is_active: bool
    created_at: datetime | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
