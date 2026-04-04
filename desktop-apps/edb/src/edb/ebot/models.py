"""Models for ebot natural language query interface."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class NLQuery(BaseModel):
    """A natural language query from the user."""
    text: str
    context: dict[str, Any] | None = None


class TranslationResult(BaseModel):
    """Result of translating a natural language query to eDB query DSL."""
    original_text: str
    translated_query: dict[str, Any] | None = None
    confidence: float = 0.0
    explanation: str = ""
    error: str | None = None
