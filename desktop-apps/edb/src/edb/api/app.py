"""FastAPI application factory and dependencies for eDB."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from edb.api.dependencies import AppState
from edb.api.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from edb.api.routes import admin, auth, documents, ebot, graph, kv, sql
from edb.config import EDBConfig


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config = EDBConfig()
    state = AppState(config)
    app.state.edb = state

    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))

    if config.create_admin:
        state.user_manager.ensure_admin_exists()
    yield
    state.database.close()


def create_app(config: EDBConfig | None = None) -> FastAPI:
    if config is None:
        config = EDBConfig()

    app = FastAPI(
        title="eDB API",
        description="Unified Multi-Model Database API — SQL, Document, Key-Value, Graph",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if config.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            max_requests=config.rate_limit_requests,
            window_seconds=config.rate_limit_window_seconds,
        )
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(sql.router, prefix="/sql", tags=["SQL"])
    app.include_router(documents.router, prefix="/docs", tags=["Documents"])
    app.include_router(kv.router, prefix="/kv", tags=["Key-Value"])
    app.include_router(graph.router, prefix="/graph", tags=["Graph"])
    app.include_router(admin.router, prefix="/admin", tags=["Admin"])
    app.include_router(ebot.router, prefix="/ebot", tags=["ebot AI"])

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": "0.1.0"}

    return app
