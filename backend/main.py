"""
FastAPI main application for AI Matchmaker web platform.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.core.config import settings
from app.core.database import init_db
from app.core.ai_config import initialize_ai_services
from app.api.v1.api import api_router
from app.websocket.manager import router as websocket_router
from app.websocket.events import start_websocket_events, stop_websocket_events

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI Matchmaker application...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize AI services
    ai_status = initialize_ai_services()
    logger.info(f"AI services initialization: {ai_status}")
    
    # Start WebSocket events
    await start_websocket_events()
    logger.info("WebSocket events started")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await stop_websocket_events()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="AI Matchmaker API",
    description="AI-powered matchmaking platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_hosts(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")

# Serve static files in production
if settings.ENVIRONMENT == "production":
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.core.ai_config import get_ai_service_status
    
    ai_status = get_ai_service_status()
    
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "ai_services": ai_status
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )