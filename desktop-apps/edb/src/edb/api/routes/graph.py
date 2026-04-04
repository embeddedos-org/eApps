"""Graph API routes for eDB."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from edb.api.dependencies import AppState, get_app_state, require_permission
from edb.auth.models import Permission

router = APIRouter()


class AddNodeRequest(BaseModel):
    label: str
    properties: dict[str, Any] | None = None
    node_id: str | None = None


class AddEdgeRequest(BaseModel):
    source_id: str
    target_id: str
    relationship: str
    properties: dict[str, Any] | None = None


class TraverseRequest(BaseModel):
    start_id: str
    relationship: str | None = None
    depth: int = 1


@router.post("/nodes", status_code=status.HTTP_201_CREATED)
def add_node(
    request: AddNodeRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    node = state.database.graph.add_node(request.label, request.properties, request.node_id)
    return node


@router.get("/nodes/{node_id}")
def get_node(
    node_id: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, Any]:
    node = state.database.graph.get_node(node_id)
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node


@router.get("/nodes")
def find_nodes(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
    label: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    nodes = state.database.graph.find_nodes(label, limit)
    return {"nodes": nodes, "count": len(nodes)}


@router.delete("/nodes/{node_id}")
def delete_node(
    node_id: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_DELETE))],
) -> dict[str, bool]:
    deleted = state.database.graph.delete_node(node_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return {"deleted": True}


@router.post("/edges", status_code=status.HTTP_201_CREATED)
def add_edge(
    request: AddEdgeRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    edge = state.database.graph.add_edge(
        request.source_id, request.target_id, request.relationship, request.properties,
    )
    return edge


@router.get("/nodes/{node_id}/edges")
def get_edges(
    node_id: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
    direction: str = "both",
    relationship: str | None = None,
) -> dict[str, Any]:
    edges = state.database.graph.get_edges(node_id, direction, relationship)
    return {"edges": edges, "count": len(edges)}


@router.post("/traverse")
def traverse(
    request: TraverseRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, Any]:
    nodes = state.database.graph.traverse(request.start_id, request.relationship, request.depth)
    return {"nodes": nodes, "count": len(nodes)}


@router.get("/stats")
def graph_stats(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, int]:
    return {
        "node_count": state.database.graph.node_count(),
        "edge_count": state.database.graph.edge_count(),
    }
