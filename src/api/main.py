"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import close_db, get_engine, init_db

from .routes import articles_router, crawlers_router, feed_router
from .schemas import HealthResponse

# Application version (sync with pyproject.toml)
VERSION = "2.2.1"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup/shutdown."""
    # Startup: Initialize database engine
    get_engine()
    yield
    # Shutdown: Close database connections
    await close_db()


app = FastAPI(
    title="핫딜 API",
    description="한국 커뮤니티 핫딜 모아보기 API",
    version=VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(articles_router, prefix="/api/v1")
app.include_router(crawlers_router, prefix="/api/v1")
app.include_router(feed_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version=VERSION)


@app.get("/", include_in_schema=False)
async def root() -> dict:
    """Root endpoint redirect to docs."""
    return {
        "message": "핫딜 API",
        "version": VERSION,
        "docs": "/docs",
        "health": "/health",
    }
