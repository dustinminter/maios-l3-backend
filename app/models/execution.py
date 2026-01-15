from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStatusEnum(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class TaskProgress(BaseModel):
    """Progress information for a single task."""
    task_id: str
    task_type: str
    description: str
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    percent: int = 0
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    error: Optional[str] = None


class Artifact(BaseModel):
    """An output artifact from execution."""
    artifact_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: Literal["document", "data", "image", "code", "markdown"]
    filename: str
    mime_type: str
    size_bytes: Optional[int] = None
    content: Optional[str] = None  # For inline content (markdown, small data)
    download_url: Optional[str] = None
    preview_text: Optional[str] = None
    produced_by: str  # task_id
    produced_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionRequest(BaseModel):
    """Request to execute an orchestration plan."""
    intent: str = Field(..., description="The user's intent or task description")
    task_type: str = Field(default="rfx_analysis", description="Type of task to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")
    document_content: Optional[str] = Field(None, description="Document content if applicable")
    user_id: Optional[str] = Field(default="anonymous", description="User identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "Analyze this RFP and create a compliance matrix",
                "task_type": "rfx_analysis",
                "parameters": {},
                "user_id": "user_123"
            }
        }


class ExecutionSummary(BaseModel):
    """Summary of execution results."""
    tasks_total: int
    tasks_completed: int
    tasks_failed: int
    total_duration_ms: int
    total_tokens: int
    estimated_cost: float


class TaskStatus(BaseModel):
    """Status of a single task in execution."""
    task_id: str
    task_type: str
    description: str
    status: TaskStatusEnum
    progress: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    output_preview: Optional[str] = None


class ExecutionStatus(BaseModel):
    """Full status of an execution."""
    execution_id: str
    status: ExecutionStatusEnum
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Task breakdown
    tasks: List[TaskStatus] = []
    current_task: Optional[str] = None

    # Progress
    overall_progress: int = 0
    message: Optional[str] = None

    # Results
    summary: Optional[ExecutionSummary] = None
    artifacts: List[Artifact] = []

    # Errors
    errors: List[str] = []


class ExecutionResponse(BaseModel):
    """Response after starting an execution."""
    execution_id: str
    status: ExecutionStatusEnum
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec_abc123",
                "status": "queued",
                "message": "Execution queued successfully",
                "created_at": "2025-01-15T12:00:00Z"
            }
        }
