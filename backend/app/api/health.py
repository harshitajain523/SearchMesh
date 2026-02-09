"""
Health API Routes

System health and status endpoints.
"""
from fastapi import APIRouter
from app.core.circuit_breaker import circuit_registry
from app.engines.aggregator import aggregator

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with component status."""
    return {
        "status": "healthy",
        "engines": aggregator.get_engine_status(),
        "circuit_breakers": circuit_registry.get_all_stats(),
    }
