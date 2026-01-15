"""Core orchestration service that executes task plans."""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from app.models import (
    ExecutionRequest,
    ExecutionStatus,
    ExecutionStatusEnum,
    TaskStatus,
    TaskStatusEnum,
    TaskProgress,
    Artifact,
    ExecutionSummary,
)
from app.services.store import execution_store
from app.config import settings


class OrchestrationService:
    """
    Orchestrates task execution for MAIOS L3.

    For MVP/demo: Simulates execution with realistic timing.
    For production: Integrates with Claude, document generators, etc.
    """

    def __init__(self):
        self.store = execution_store

    def _get_rfx_tasks(self) -> List[Dict[str, Any]]:
        """Get task definitions for RFx analysis workflow."""
        return [
            {
                "task_id": "parse_document",
                "task_type": "document.parse",
                "description": "Parse and structure the document",
                "duration_ms": 2000,
                "tokens": 0,
            },
            {
                "task_id": "extract_requirements",
                "task_type": "analysis.extract",
                "description": "Extract requirements from document",
                "duration_ms": 5000,
                "tokens": 4200,
            },
            {
                "task_id": "extract_eval_criteria",
                "task_type": "analysis.extract",
                "description": "Extract evaluation criteria",
                "duration_ms": 4000,
                "tokens": 2100,
            },
            {
                "task_id": "compliance_mapping",
                "task_type": "analysis.mapping",
                "description": "Map requirements to compliance standards",
                "duration_ms": 6000,
                "tokens": 3500,
            },
            {
                "task_id": "generate_matrix",
                "task_type": "document.generate",
                "description": "Generate compliance matrix",
                "duration_ms": 3000,
                "tokens": 1500,
            },
        ]

    async def execute(self, request: ExecutionRequest) -> ExecutionStatus:
        """
        Start execution of a task plan.

        Returns immediately with execution_id, processes in background.
        """
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"

        # Get task definitions based on task type
        if request.task_type == "rfx_analysis":
            task_defs = self._get_rfx_tasks()
        else:
            task_defs = self._get_rfx_tasks()  # Default to RFx for now

        # Create initial execution status
        tasks = [
            TaskStatus(
                task_id=t["task_id"],
                task_type=t["task_type"],
                description=t["description"],
                status=TaskStatusEnum.PENDING,
                progress=0,
            )
            for t in task_defs
        ]

        execution = ExecutionStatus(
            execution_id=execution_id,
            status=ExecutionStatusEnum.QUEUED,
            created_at=datetime.utcnow(),
            tasks=tasks,
            overall_progress=0,
            message="Execution queued",
        )

        await self.store.create(execution)

        # Start background execution
        asyncio.create_task(self._run_execution(execution_id, task_defs, request))

        return execution

    async def _run_execution(
        self,
        execution_id: str,
        task_defs: List[Dict[str, Any]],
        request: ExecutionRequest
    ):
        """Run the actual execution in background."""
        execution = await self.store.get(execution_id)
        if not execution:
            return

        execution.status = ExecutionStatusEnum.RUNNING
        execution.started_at = datetime.utcnow()
        execution.message = "Execution started"
        await self.store.update(execution)

        total_tokens = 0
        start_time = datetime.utcnow()
        completed_count = 0
        failed_count = 0

        for i, task_def in enumerate(task_defs):
            task_id = task_def["task_id"]

            # Update current task
            execution.current_task = task_id

            # Find and update task status
            for task in execution.tasks:
                if task.task_id == task_id:
                    task.status = TaskStatusEnum.RUNNING
                    task.started_at = datetime.utcnow()
                    task.progress = 0
                    break

            execution.message = f"Running: {task_def['description']}"
            await self.store.update(execution)

            # Simulate task execution with progress updates
            duration_ms = task_def["duration_ms"]
            steps = 5
            step_duration = duration_ms / steps / 1000

            for step in range(steps):
                await asyncio.sleep(step_duration)

                # Update task progress
                for task in execution.tasks:
                    if task.task_id == task_id:
                        task.progress = int((step + 1) / steps * 100)
                        break

                # Update overall progress
                execution.overall_progress = int(
                    ((i * 100) + (step + 1) / steps * 100) / len(task_defs)
                )
                await self.store.update(execution)

            # Mark task complete
            for task in execution.tasks:
                if task.task_id == task_id:
                    task.status = TaskStatusEnum.COMPLETED
                    task.completed_at = datetime.utcnow()
                    task.progress = 100
                    break

            total_tokens += task_def.get("tokens", 0)
            completed_count += 1
            await self.store.update(execution)

        # Generate artifacts
        artifacts = await self._generate_artifacts(execution_id, request)
        execution.artifacts = artifacts

        # Calculate summary
        end_time = datetime.utcnow()
        total_duration = int((end_time - start_time).total_seconds() * 1000)

        execution.summary = ExecutionSummary(
            tasks_total=len(task_defs),
            tasks_completed=completed_count,
            tasks_failed=failed_count,
            total_duration_ms=total_duration,
            total_tokens=total_tokens,
            estimated_cost=total_tokens * 0.00001,  # Rough estimate
        )

        # Mark execution complete
        execution.status = ExecutionStatusEnum.COMPLETED
        execution.completed_at = datetime.utcnow()
        execution.current_task = None
        execution.overall_progress = 100
        execution.message = "Execution completed successfully"
        await self.store.update(execution)

    async def _generate_artifacts(
        self,
        execution_id: str,
        request: ExecutionRequest
    ) -> List[Artifact]:
        """Generate output artifacts."""
        artifacts = []

        # Generate compliance matrix artifact
        matrix_content = self._generate_compliance_matrix(request)

        artifacts.append(Artifact(
            artifact_type="markdown",
            filename="compliance_matrix.md",
            mime_type="text/markdown",
            content=matrix_content,
            size_bytes=len(matrix_content.encode()),
            preview_text=matrix_content[:500] + "..." if len(matrix_content) > 500 else matrix_content,
            produced_by="generate_matrix",
        ))

        # Generate executive summary
        summary_content = self._generate_executive_summary(request)

        artifacts.append(Artifact(
            artifact_type="markdown",
            filename="executive_summary.md",
            mime_type="text/markdown",
            content=summary_content,
            size_bytes=len(summary_content.encode()),
            preview_text=summary_content[:300] + "..." if len(summary_content) > 300 else summary_content,
            produced_by="extract_requirements",
        ))

        return artifacts

    def _generate_compliance_matrix(self, request: ExecutionRequest) -> str:
        """Generate a compliance matrix based on the request."""
        return f"""# Compliance Matrix

**Generated:** {datetime.utcnow().isoformat()}Z
**Intent:** {request.intent}

---

## Requirements Traceability

| Req ID | Requirement | Category | Priority | Compliance Standard | Status |
|--------|-------------|----------|----------|---------------------|--------|
| REQ-001 | System shall provide real-time data analytics | Technical | Mandatory | NIST 800-53 AC-2 | Compliant |
| REQ-002 | Solution must support FedRAMP authorization | Compliance | Mandatory | FedRAMP Moderate | In Progress |
| REQ-003 | Vendor shall provide 24/7 support | Management | Mandatory | SLA Requirements | Compliant |
| REQ-004 | System should integrate with existing ERP | Technical | Desired | Integration Standards | Partial |
| REQ-005 | Solution must include data encryption at rest | Security | Mandatory | NIST 800-53 SC-28 | Compliant |
| REQ-006 | Reporting dashboards required | Functional | Mandatory | User Requirements | Compliant |
| REQ-007 | Mobile access capability | Technical | Optional | Accessibility | Not Started |
| REQ-008 | Automated backup and recovery | Operations | Mandatory | NIST 800-53 CP-9 | Compliant |

---

## Compliance Summary

| Standard | Total Controls | Compliant | Partial | Gap |
|----------|---------------|-----------|---------|-----|
| NIST 800-53 | 12 | 10 | 1 | 1 |
| FedRAMP | 8 | 6 | 2 | 0 |
| SOC 2 | 5 | 5 | 0 | 0 |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| FedRAMP timeline | Medium | High | Engage 3PAO early |
| Integration complexity | Low | Medium | Phased approach |
| Resource availability | Medium | Medium | Staff augmentation plan |

---

## Recommendations

1. **Prioritize FedRAMP documentation** - Critical path item
2. **Engage integration team early** - REQ-004 needs attention
3. **Mobile capability assessment** - Defer to Phase 2 if optional

---

*Generated by MAIOS L3 Orchestration Engine*
"""

    def _generate_executive_summary(self, request: ExecutionRequest) -> str:
        """Generate an executive summary."""
        return f"""# Executive Summary

**Analysis Date:** {datetime.utcnow().strftime("%Y-%m-%d")}
**Request:** {request.intent}

---

## Overview

This analysis identified **8 requirements** across technical, compliance, and management categories. The opportunity shows strong alignment with existing capabilities, with **75% immediate compliance** and clear paths to address gaps.

## Key Findings

### Strengths
- Strong technical alignment with core requirements
- Existing compliance certifications cover majority of needs
- Proven past performance in similar engagements

### Gaps Identified
- FedRAMP authorization timeline needs acceleration
- ERP integration requires technical assessment
- Mobile capability not currently available

## Recommendation

**Pursue** — This opportunity aligns well with capabilities. Focus proposal on compliance strengths and provide clear mitigation plan for identified gaps.

## Next Steps

1. Assign capture lead
2. Schedule technical review for integration requirements
3. Initiate FedRAMP acceleration activities
4. Draft response outline

---

*Generated by MAIOS L3 Orchestration Engine*
"""

    async def get_status(self, execution_id: str) -> Optional[ExecutionStatus]:
        """Get the current status of an execution."""
        return await self.store.get(execution_id)

    async def list_executions(
        self,
        user_id: Optional[str] = None,
        status: Optional[ExecutionStatusEnum] = None,
        limit: int = 50
    ) -> List[ExecutionStatus]:
        """List executions with optional filters."""
        return await self.store.list_all(user_id=user_id, status=status, limit=limit)


# Global service instance
orchestration_service = OrchestrationService()
