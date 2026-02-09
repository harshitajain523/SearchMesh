"""
SearchMesh - Federated Search Engine

Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import api_router
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Log configured engines
    engines_status = []
    if settings.google_api_key:
        engines_status.append("Google ✓")
    else:
        engines_status.append("Google ✗ (no API key)")
    
    if settings.bing_api_key:
        engines_status.append("Bing ✓")
    else:
        engines_status.append("Bing ✗ (no API key)")
    
    engines_status.append("DuckDuckGo ✓ (no key needed)")
    
    logger.info(f"Search engines: {', '.join(engines_status)}")
    
    yield
    
    logger.info(f"Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="Federated search engine with intelligent deduplication and rule-based filtering",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix=settings.api_prefix)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.app_name,
            "version": "1.0.0",
            "docs": "/docs",
            "api": settings.api_prefix,
        }
    
    return app


# Create app instance
app = create_app()
