"""
LokMat API — Health router.

GET /health — DB + Gemini + Redis connectivity check.
Used by Cloud Run readiness probe.
"""

from fastapi import APIRouter

from api.config import settings
from api.schemas.schemas import HealthResponse
from api.services.gemini_service import check_health as check_gemini_health

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Returns service health status.

    Checks:
    - Database (Cloud SQL) connectivity
    - Gemini API connectivity
    - Redis (Memorystore) connectivity
    """
    # Check Database
    try:
        from api.db.session import check_db_connection
        db_ok = await check_db_connection()
    except Exception:
        db_ok = False

    # Check Gemini (Fast stateless check)
    gemini_health = await check_gemini_health()
    gemini_ok = gemini_health["status"] == "ok"

    # Check Redis
    try:
        from api.services.cache_service import cache_service
        redis_ok = await cache_service.health_check()
    except Exception:
        redis_ok = False

    status = "ok" if (db_ok and gemini_ok) else "degraded"

    return HealthResponse(
        status=status,
        db="ok" if db_ok else "error",
        gemini="ok" if gemini_ok else "error",
        redis="ok" if redis_ok else "error",
        version=settings.app_version,
    )
