"""eDB configuration management.

Uses Pydantic Settings to load configuration from environment variables and .env files.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings


class EDBConfig(BaseSettings):
    """eDB configuration loaded from environment variables."""

    db_path: str = Field(default="edb_data.db", description="Path to the SQLite database file")
    api_host: str = Field(default="127.0.0.1", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_reload: bool = Field(default=False, description="Enable auto-reload for development")

    jwt_secret: str = Field(
        default="edb-secret-change-me-in-production",
        description="Secret key for JWT token signing",
    )
    jwt_access_expire_minutes: int = Field(
        default=60, description="Access token expiration in minutes"
    )
    jwt_refresh_expire_days: int = Field(default=7, description="Refresh token expiration in days")

    encryption_key: str = Field(
        default="edb-encryption-key-change-me",
        description="Encryption key for data at rest",
    )

    log_level: str = Field(default="INFO", description="Logging level")
    audit_enabled: bool = Field(default=True, description="Enable audit logging")
    create_admin: bool = Field(default=True, description="Auto-create default admin user")

    rate_limit_enabled: bool = Field(default=True, description="Enable API rate limiting")
    rate_limit_requests: int = Field(default=100, description="Max requests per window")
    rate_limit_window_seconds: int = Field(default=60, description="Rate limit window in seconds")

    ebot_enabled: bool = Field(default=True, description="Enable ebot AI query interface")
    ebot_provider: str = Field(
        default="rule_based", description="ebot provider: rule_based or openai"
    )
    ebot_openai_api_key: str = Field(default="", description="OpenAI API key for ebot LLM mode")
    ebot_openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model for ebot")

    model_config = {
        "env_prefix": "EDB_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }
