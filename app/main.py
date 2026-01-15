"""
MAIOS L3 Orchestration Engine

FastAPI application that orchestrates task execution across AI models,
document generators, and external tools.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import orchestration_router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## MAIOS L3 Orchestration Engine

The execution layer that turns plans into outcomes. Manages task execution
across AI models, software tools, and external APIs.

### Key Endpoints

- **POST /orchestration/execute** - Start a new execution
- **GET /orchestration/status/{id}** - Get execution status
- **GET /orchestration/executions** - List recent executions

### Example Flow

1. POST to `/orchestration/execute` with your intent
2. Receive `execution_id` immediately
3. Poll `/orchestration/status/{execution_id}` for progress
4. When complete, status includes artifacts
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(orchestration_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
