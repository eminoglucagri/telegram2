"""FastAPI application main module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from src.core.config import settings
from src.database.base import init_db, close_db
from src.utils.logger import setup_logging
from .routes import (
    accounts,
    campaigns,
    groups,
    messages,
    leads,
    analytics,
    settings as settings_routes,
    personas,
    warmup
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    setup_logging()
    logger.info("Starting Telegram Agent API...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(
    title="Telegram Stealth Marketing Agent",
    description="API for managing Telegram marketing automation",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(settings_routes.router, prefix="/api/settings", tags=["Settings"])
app.include_router(personas.router, prefix="/api/personas", tags=["Personas"])
app.include_router(warmup.router, prefix="/api/warmup", tags=["Warm-up"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Telegram Stealth Marketing Agent",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
