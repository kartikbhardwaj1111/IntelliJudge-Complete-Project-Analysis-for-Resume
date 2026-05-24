"""
IntelliJudge — FastAPI Application Entry Point

When you run:
    uvicorn app.main:app --reload --port 8000

...uvicorn looks for the `app` variable in this file and starts the server.

KEY CONCEPTS:
  1. FastAPI()          — creates the application instance
  2. CORS Middleware    — allows the Next.js frontend to call our API
  3. Exception Handlers — catches errors and returns consistent JSON responses
  4. Lifespan          — startup: verify DB connection; shutdown: close pool
  5. Route Registration — each phase's router is added here with a URL prefix
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import AsyncSessionLocal
from app.utils.exceptions import AppException, error_response, success_response


# ─── Lifespan (Startup / Shutdown) ─────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    print(f"📄 Swagger docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔧 Debug mode:   {settings.DEBUG}")

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        print("✅ Database connection verified")
    except Exception as exc:
        print(f"⚠️  Database not reachable: {exc}")
        print("   → Set DATABASE_URL in .env and restart to enable DB features")

    try:
        from app.services.ocr_service import _get_ocr_reader
        print("⏳ Loading EasyOCR model (first run downloads ~100 MB, please wait)...")
        await asyncio.to_thread(_get_ocr_reader)
        print("✅ EasyOCR model ready")
    except Exception as exc:
        print(f"⚠️  EasyOCR pre-warm failed: {exc}")
        print("   → First upload request will be slow while model downloads")

    yield

    print(f"\n👋 {settings.APP_NAME} shutting down...")


# ─── Create FastAPI Application ────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Powered Coding Question Recovery & Practice Platform. "
        "Upload a screenshot of a coding problem → get a reconstructed "
        "problem statement → solve it with an integrated code editor."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─── CORS Middleware ───────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Exception Handlers ────────────────────────────────
#
# FastAPI's CORSMiddleware does not reliably inject CORS headers into
# responses that are generated inside exception handlers (the middleware
# wraps the `send` callable, but some Starlette versions short-circuit
# before the wrapper fires for error paths).  We therefore add the
# Access-Control-Allow-Origin header manually here so that the browser
# can always read the error body — otherwise a 400/500 looks like a
# "CORS blocked" failure in the console even though the backend is fine.

def _cors_headers(request: Request) -> dict:
    """Return CORS headers for the request's Origin if it is allowed."""
    origin = request.headers.get("origin")
    if origin and origin in settings.CORS_ORIGINS:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.message, errors=exc.errors),
        headers=_cors_headers(request),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    message = "Internal server error"
    if settings.DEBUG:
        message = f"Internal server error: {str(exc)}"
    return JSONResponse(
        status_code=500,
        content=error_response(message=message),
        headers=_cors_headers(request),
    )


# ─── System Routes ─────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """Verify the API is alive and report DB status."""
    db_status = "unknown"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "unreachable"

    return success_response(
        message=f"{settings.APP_NAME} API is running",
        data={
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — directs developers to the API docs."""
    return success_response(
        message=f"Welcome to {settings.APP_NAME}! Visit /docs for API documentation.",
        data={"docs": "/docs", "health": "/health"},
    )


# ─── Route Registration ────────────────────────────────────────

# Phase 3 — Auth
from app.routes.auth import router as auth_router  # noqa: E402
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

# Phase 4 — Upload & OCR
from app.routes.upload import router as upload_router  # noqa: E402
app.include_router(upload_router, prefix="/api/upload", tags=["Upload"])

# Phase 5 — Problems (CRUD + AI Reconstruction + Test Case Generation)
from app.routes.problems import router as problems_router  # noqa: E402
app.include_router(problems_router, prefix="/api/problems", tags=["Problems"])

# Phase 8 — Submissions
from app.routes.submissions import router as submissions_router  # noqa: E402
app.include_router(submissions_router, prefix="/api/submissions", tags=["Submissions"])

# Phase 9 — AI Features
from app.routes.ai import router as ai_router  # noqa: E402
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])

# Phase 10 — Analytics
from app.routes.analytics import router as analytics_router  # noqa: E402
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])
