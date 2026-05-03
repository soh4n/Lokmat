"""
LokMat API — FastAPI application entry point.

Configures middleware, CORS, OpenAPI documentation, and mounts all routers.
Per GEMINI.md: structured logging, CORS allowlist, rate limiting, and proper error handling.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.routers import assistant, auth, elections, health, voter
from api.utils.logging import setup_cloud_logging
from api.utils.rate_limit import RateLimitMiddleware

# --- Structured Cloud Logging ---
setup_cloud_logging(debug=settings.debug)
logger = logging.getLogger("lokmat")


# --- Lifespan ---
@asynccontextmanager  # type: ignore
async def lifespan(app: FastAPI) -> None:  # type: ignore
    """Application startup and shutdown events."""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    logger.info(f"   Gemini model: {settings.gemini_model_flash}")
    logger.info(f"   CORS origins: {settings.cors_origins}")
    logger.info(f"   Database: {settings.database_url[:30]}...")

    # Initialize database tables
    try:
        from api.db.session import init_db
        await init_db()
        logger.info("   ✅ Database initialized")
    except Exception as e:
        logger.warning(f"   ⚠️ Database init skipped (will use in-memory): {e}")

    # Initialize cache service
    try:
        from api.services.cache_service import cache_service
        cache_service.__init__(settings.redis_url or None)  # type: ignore
        logger.info("   ✅ Cache service initialized")
    except Exception as e:
        logger.warning(f"   ⚠️ Cache init skipped: {e}")

    yield
    logger.info(f"👋 {settings.app_name} shutting down.")


# --- App ---
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "LokMat (लोकमत) — AI-powered election companion API for Indian voters. "
        "Provides voter profile management, AI-assisted election guidance via VoteSathi AI, "
        "booth information, and emergency services. "
        "Built with Gemini Flash, Cloud SQL, Memorystore, Cloud Logging, and Cloud Run."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# --- Middleware Stack (order matters: outermost first) ---

# Rate limiting (per GEMINI.md security)
app.add_middleware(RateLimitMiddleware)

# CORS (per GEMINI.md: allowlist only production frontend origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next) -> None:  # type: ignore
    """Log every request with method, path, status, and latency."""
    start = time.perf_counter()
    response = await call_next(request)
    latency = round((time.perf_counter() - start) * 1000, 2)

    logger.info(
        "http_request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency,
        },
    )
    return response  # type: ignore


# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> None:
    """
    Catch-all exception handler.
    Never surface raw exceptions to users per GEMINI.md security rules.
    """
    logger.error(
        "unhandled_error",
        extra={
            "method": request.method,
            "path": request.url.path,
            "error": str(exc),
        },
    )
    return JSONResponse(  # type: ignore
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "support": "Call 1950 for immediate assistance.",
        },
    )


# --- Mount Routers ---
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(voter.router)
app.include_router(assistant.router)
app.include_router(elections.router)


# --- Root ---
@app.get("/", tags=["Root"])
async def root() -> None:
    """API root endpoint with welcome message."""
    return {  # type: ignore
        "name": settings.app_name,
        "version": settings.app_version,
        "message": "Welcome to LokMat API — Your Election Companion 🗳️",
        "docs": "/docs",
        "services": [
            "Gemini AI (Flash + Pro)",
            "Cloud SQL (PostgreSQL)",
            "Memorystore (Redis)",
            "Cloud Logging",
            "Cloud Storage",
            "Cloud Run",
        ],
    }
