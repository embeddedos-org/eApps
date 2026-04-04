"""Document store API routes for eDB."""

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


class DocumentInsertRequest(BaseModel):
    data: dict[str, Any]
    doc_id: str | None = None


class DocumentUpdateRequest(BaseModel):
    data: dict[str, Any]
    merge: bool = True


class DocumentFilterRequest(BaseModel):
    filter: dict[str, Any] | None = None
    limit: int | None = None
    offset: int | None = None


@router.get("/collections")
def list_collections(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, list[str]]:
    """List all document collections."""
    collections = state.database.docs.list_collections()
    return {"collections": collections}


@router.post("/{collection}", status_code=status.HTTP_201_CREATED)
def insert_document(
    collection: str,
    request: DocumentInsertRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    """Insert a document into a collection."""
    doc = state.database.docs.insert(collection, request.data, request.doc_id)
    state.audit.log(
        event_type="query",
        action="doc_insert",
        user_id=user.get("sub"),
        details={"collection": collection, "doc_id": doc.id},
    )
    return doc.model_dump(mode="json")


@router.post("/{collection}/find")
def find_documents(
    collection: str,
    request: DocumentFilterRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, Any]:
    """Find documents matching a filter."""
    docs = state.database.docs.find(
        collection=collection,
        filter_dict=request.filter,
        limit=request.limit,
        offset=request.offset,
    )
    return {
        "documents": [d.model_dump(mode="json") for d in docs],
        "count": len(docs),
    }


@router.get("/{collection}/{doc_id}")
def get_document(
    collection: str,
    doc_id: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, Any]:
    """Get a document by ID."""
    doc = state.database.docs.find_by_id(collection, doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc.model_dump(mode="json")


@router.put("/{collection}/{doc_id}")
def update_document(
    collection: str,
    doc_id: str,
    request: DocumentUpdateRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    """Update a document by ID."""
    doc = state.database.docs.update(collection, doc_id, request.data, request.merge)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    state.audit.log(
        event_type="query",
        action="doc_update",
        user_id=user.get("sub"),
        details={"collection": collection, "doc_id": doc_id},
    )
    return doc.model_dump(mode="json")


@router.delete("/{collection}/{doc_id}")
def delete_document(
    collection: str,
    doc_id: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_DELETE))],
) -> dict[str, bool]:
    """Delete a document by ID."""
    deleted = state.database.docs.delete(collection, doc_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    state.audit.log(
        event_type="query",
        action="doc_delete",
        user_id=user.get("sub"),
        details={"collection": collection, "doc_id": doc_id},
    )
    return {"deleted": True}
