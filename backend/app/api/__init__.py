"""API module exports."""
from fastapi import APIRouter

from app.api.search import router as search_router
from app.api.health import router as health_router

# Main API router
api_router = APIRouter()
api_router.include_router(search_router)
api_router.include_router(health_router)

__all__ = ["api_router"]
