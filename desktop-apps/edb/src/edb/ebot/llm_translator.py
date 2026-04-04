"""LLM-powered natural language query translator for ebot.

Uses OpenAI-compatible API to translate natural language to eDB query DSL.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from edb.ebot.models import TranslationResult

logger = logging.getLogger("edb.ebot.llm")

SYSTEM_PROMPT = """You are ebot, a query translator for eDB — a multi-model database.
Translate the user's natural language query into a JSON query object.

Available query types:
1. SQL: {"type": "sql", "action": "select|insert|update|delete",
   "table": "...", "columns": [...], "where": {...}, "data": {...}}
2. Document: {"type": "document", "action": "find|insert|update|delete|count",
   "collection": "...", "filter": {...}, "data": {...}}
3. Key-Value: {"type": "kv", "action": "get|set|delete|list", "key": "...", "value": ...}

Return ONLY valid JSON. No explanation or markdown."""


class LLMTranslator:
    """Translates natural language queries using an OpenAI-compatible LLM."""

    def __init__(
        self, api_key: str, model: str = "gpt-3.5-turbo",
        base_url: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url

    def translate(self, text: str, context: dict[str, Any] | None = None) -> TranslationResult:
        try:
            import openai
        except ImportError:
            return TranslationResult(
                original_text=text,
                error="OpenAI package not installed. Install with: pip install edb[ebot]",
            )

        try:
            client_kwargs: dict[str, Any] = {"api_key": self._api_key}
            if self._base_url:
                client_kwargs["base_url"] = self._base_url

            client = openai.OpenAI(**client_kwargs)

            user_msg = text
            if context:
                user_msg += f"\n\nContext: {json.dumps(context)}"

            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.1,
                max_tokens=500,
            )

            content = response.choices[0].message.content or ""
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            query = json.loads(content)
            return TranslationResult(
                original_text=text,
                translated_query=query,
                confidence=0.8,
                explanation=f"LLM-generated query ({self._model})",
            )

        except json.JSONDecodeError as e:
            logger.warning("LLM returned invalid JSON: %s", e)
            return TranslationResult(original_text=text, error=f"LLM returned invalid JSON: {e}")
        except Exception as e:
            logger.error("LLM translation failed: %s", e)
            return TranslationResult(original_text=text, error=f"LLM error: {e}")
