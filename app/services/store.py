"""In-memory execution store. Replace with Redis/Snowflake for production."""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from app.models import ExecutionStatus, ExecutionStatusEnum


class ExecutionStore:
    """
    In-memory store for execution state.

    For production, replace with Redis or Snowflake.
    """

    def __init__(self):
        self._executions: Dict[str, ExecutionStatus] = {}
        self._lock = asyncio.Lock()

    async def create(self, execution: ExecutionStatus) -> ExecutionStatus:
        """Create a new execution record."""
        async with self._lock:
            self._executions[execution.execution_id] = execution
            return execution

    async def get(self, execution_id: str) -> Optional[ExecutionStatus]:
        """Get execution by ID."""
        return self._executions.get(execution_id)

    async def update(self, execution: ExecutionStatus) -> ExecutionStatus:
        """Update an execution record."""
        async with self._lock:
            self._executions[execution.execution_id] = execution
            return execution

    async def list_all(
        self,
        user_id: Optional[str] = None,
        status: Optional[ExecutionStatusEnum] = None,
        limit: int = 50
    ) -> List[ExecutionStatus]:
        """List executions with optional filters."""
        results = list(self._executions.values())

        # Filter by status if provided
        if status:
            results = [e for e in results if e.status == status]

        # Sort by created_at descending
        results.sort(key=lambda x: x.created_at, reverse=True)

        # Apply limit
        return results[:limit]

    async def delete(self, execution_id: str) -> bool:
        """Delete an execution record."""
        async with self._lock:
            if execution_id in self._executions:
                del self._executions[execution_id]
                return True
            return False


# Global store instance
execution_store = ExecutionStore()
