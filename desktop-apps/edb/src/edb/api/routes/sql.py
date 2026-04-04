"""SQL API routes for eDB."""

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


class SQLExecuteRequest(BaseModel):
    sql: str
    params: list[Any] | None = None


class CreateTableRequest(BaseModel):
    name: str
    columns: list[dict[str, Any]]


class InsertRequest(BaseModel):
    data: dict[str, Any]


class UpdateRequest(BaseModel):
    data: dict[str, Any]
    where: dict[str, Any]


class DeleteRequest(BaseModel):
    where: dict[str, Any]


class SelectRequest(BaseModel):
    columns: list[str] | None = None
    where: dict[str, Any] | None = None
    order_by: str | None = None
    limit: int | None = None
    offset: int | None = None


@router.post("/execute")
def execute_sql(
    request: SQLExecuteRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    """Execute raw SQL (requires write permission)."""
    warnings = state.validator.validate_query_input({"sql": request.sql})
    if warnings:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=warnings)

    try:
        params = tuple(request.params) if request.params else None
        result = state.database.sql.execute_raw(request.sql, params)
        state.audit.log(
            event_type="query",
            action="sql_execute",
            user_id=user.get("sub"),
            username=user.get("username"),
            details={"sql": request.sql[:200]},
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/tables")
def create_table(
    request: CreateTableRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_CREATE_TABLE))],
) -> dict[str, str]:
    """Create a new SQL table."""
    from edb.core.models import ColumnDefinition, TableSchema

    try:
        columns = [ColumnDefinition(**col) for col in request.columns]
        schema = TableSchema(name=request.name, columns=columns)
        state.database.sql.create_table(schema)
        state.audit.log(
            event_type="schema",
            action="table_created",
            user_id=user.get("sub"),
            details={"table": request.name},
        )
        return {"message": f"Table '{request.name}' created"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get("/tables")
def list_tables(
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, list[str]]:
    """List all SQL tables."""
    tables = state.database.sql.list_tables()
    return {"tables": tables}


@router.get("/tables/{table_name}")
def get_table_data(
    table_name: str,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Get data from a table."""
    try:
        rows = state.database.sql.select(table_name, limit=limit, offset=offset)
        cols = list(rows[0].keys()) if rows else []
        return {"columns": cols, "rows": rows, "row_count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/tables/{table_name}/select")
def select_from_table(
    table_name: str,
    request: SelectRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_READ))],
) -> dict[str, Any]:
    """Select rows from a table with filtering."""
    try:
        rows = state.database.sql.select(
            table=table_name,
            columns=request.columns,
            where=request.where,
            order_by=request.order_by,
            limit=request.limit,
            offset=request.offset,
        )
        cols = list(rows[0].keys()) if rows else []
        return {"columns": cols, "rows": rows, "row_count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/tables/{table_name}/insert")
def insert_into_table(
    table_name: str,
    request: InsertRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    """Insert a row into a table."""
    try:
        last_row_id = state.database.sql.insert(table_name, request.data)
        state.audit.log(
            event_type="query",
            action="sql_insert",
            user_id=user.get("sub"),
            details={"table": table_name},
        )
        return {"last_row_id": last_row_id, "affected_rows": 1}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.put("/tables/{table_name}/update")
def update_table(
    table_name: str,
    request: UpdateRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_WRITE))],
) -> dict[str, Any]:
    """Update rows in a table."""
    try:
        affected = state.database.sql.update(table_name, request.data, request.where)
        state.audit.log(
            event_type="query",
            action="sql_update",
            user_id=user.get("sub"),
            details={"table": table_name},
        )
        return {"affected_rows": affected}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete("/tables/{table_name}/delete")
def delete_from_table(
    table_name: str,
    request: DeleteRequest,
    state: Annotated[AppState, Depends(get_app_state)],
    user: Annotated[dict[str, Any], Depends(require_permission(Permission.DB_DELETE))],
) -> dict[str, Any]:
    """Delete rows from a table."""
    try:
        affected = state.database.sql.delete(table_name, request.where)
        state.audit.log(
            event_type="query",
            action="sql_delete",
            user_id=user.get("sub"),
            details={"table": table_name},
        )
        return {"affected_rows": affected}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
