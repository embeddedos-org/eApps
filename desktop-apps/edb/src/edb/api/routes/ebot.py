"""ebot API routes for natural language querying."""

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
from edb.ebot.sanitizer import PromptSanitizer
from edb.ebot.translator import NLQueryTranslator
from edb.query.parser import QueryParser
from edb.query.planner import QueryPlanner

router = APIRouter()


class EbotQueryRequest(BaseModel):
    text: str
    execute: bool = True


@router.post("/query")
def ebot_query(
    request: EbotQueryRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.EBOT_QUERY))],
) -> dict[str, Any]:
    """Execute a natural language query via ebot."""
    sanitizer = PromptSanitizer()
    sanitized_text, warnings = sanitizer.sanitize_input(request.text)

    if warnings:
        state.audit.log(
            event_type="security",
            action="ebot_injection_attempt",
            user_id=user.get("sub"),
            details={"text": request.text[:100], "warnings": warnings},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Query rejected", "warnings": warnings},
        )

    translator = NLQueryTranslator(provider=state.config.ebot_provider)
    translation = translator.translate(sanitized_text)

    if translation.error:
        return {
            "success": False,
            "original_text": translation.original_text,
            "error": translation.error,
        }

    user_role = user.get("role", "read_only")
    validated = sanitizer.validate_translation(translation, user_role)
    if validated.error:
        return {
            "success": False,
            "original_text": validated.original_text,
            "error": validated.error,
        }

    response: dict[str, Any] = {
        "success": True,
        "original_text": translation.original_text,
        "translated_query": translation.translated_query,
        "confidence": translation.confidence,
        "explanation": translation.explanation,
    }

    if request.execute and translation.translated_query:
        parser = QueryParser()
        planner = QueryPlanner(state.database)
        try:
            parsed = parser.parse(translation.translated_query)
            result = planner.execute(parsed)
            response["result"] = result.model_dump(mode="json")
            state.audit.log(
                event_type="ebot",
                action="nl_query_executed",
                user_id=user.get("sub"),
                details={
                    "text": sanitized_text[:100],
                    "query_type": translation.translated_query.get("type"),
                },
            )
        except Exception as e:
            response["result"] = {"success": False, "error": str(e)}

    return response
