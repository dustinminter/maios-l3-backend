"""Orchestration API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.models import (
    ExecutionRequest,
    ExecutionResponse,
    ExecutionStatus,
    ExecutionStatusEnum,
)
from app.services.orchestrator import orchestration_service


router = APIRouter(prefix="/orchestration", tags=["Orchestration"])


@router.post("/execute", response_model=ExecutionResponse)
async def execute(request: ExecutionRequest):
    """
    Start a new orchestration execution.

    Accepts an intent and task type, returns an execution_id immediately.
    Poll /status/{execution_id} for progress.

    **Example Request:**
    ```json
    {
        "intent": "Analyze this RFP and create a compliance matrix",
        "task_type": "rfx_analysis"
    }
    ```
    """
    execution = await orchestration_service.execute(request)

    return ExecutionResponse(
        execution_id=execution.execution_id,
        status=execution.status,
        message="Execution started. Poll /status/{execution_id} for progress.",
        created_at=execution.created_at,
    )


@router.get("/status/{execution_id}", response_model=ExecutionStatus)
async def get_status(execution_id: str):
    """
    Get the status of an execution.

    Returns full execution status including:
    - Overall progress (0-100)
    - Individual task statuses
    - Artifacts when complete
    - Errors if any

    **Response includes:**
    - `status`: queued, running, completed, partial, failed
    - `overall_progress`: 0-100 percentage
    - `tasks`: List of individual task statuses
    - `artifacts`: Output files when complete
    """
    execution = await orchestration_service.get_status(execution_id)

    if not execution:
        raise HTTPException(
            status_code=404,
            detail=f"Execution {execution_id} not found"
        )

    return execution


@router.get("/executions", response_model=List[ExecutionStatus])
async def list_executions(
    status: Optional[ExecutionStatusEnum] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max results to return")
):
    """
    List recent executions.

    Optionally filter by status. Returns most recent first.
    """
    return await orchestration_service.list_executions(
        status=status,
        limit=limit
    )


@router.get("/execute", response_model=dict)
async def execute_docs():
    """
    API documentation for execute endpoint.

    Returns schema and examples for the execute endpoint.
    """
    return {
        "endpoint": "POST /orchestration/execute",
        "description": "Start a new orchestration execution",
        "request_schema": {
            "intent": {
                "type": "string",
                "required": True,
                "description": "The user's intent or task description",
                "example": "Analyze this RFP and create a compliance matrix"
            },
            "task_type": {
                "type": "string",
                "required": False,
                "default": "rfx_analysis",
                "description": "Type of task to execute",
                "options": ["rfx_analysis"]
            },
            "parameters": {
                "type": "object",
                "required": False,
                "description": "Additional task parameters"
            },
            "document_content": {
                "type": "string",
                "required": False,
                "description": "Document content for analysis"
            }
        },
        "response_schema": {
            "execution_id": "string - Unique execution identifier",
            "status": "string - queued, running, completed, partial, failed",
            "message": "string - Status message",
            "created_at": "string - ISO8601 timestamp"
        },
        "example_request": {
            "intent": "Analyze this RFP and create a compliance matrix",
            "task_type": "rfx_analysis"
        },
        "example_response": {
            "execution_id": "exec_abc123def456",
            "status": "queued",
            "message": "Execution started. Poll /status/{execution_id} for progress.",
            "created_at": "2025-01-15T12:00:00Z"
        }
    }
