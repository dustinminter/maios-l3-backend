"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from app.config import settings


router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service status for load balancers and monitoring.
    """
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.get("/")
async def root():
    """Root endpoint - redirects to health."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }
