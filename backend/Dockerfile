# ============================================================
# IntelliJudge Backend — Dockerfile
# Optimised for Render free-tier deployment
# ============================================================
# Build context must be the backend/ directory:
#   docker build -t intellijudge-backend ./backend
# ============================================================

FROM python:3.11-slim

# ── Metadata ────────────────────────────────────────────────
LABEL maintainer="IntelliJudge"
LABEL description="IntelliJudge Backend API — FastAPI + SQLAlchemy"

# ── Environment ─────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── System dependencies ─────────────────────────────────────
# build-essential / gcc / g++  → compile Python C extensions
# libsm6 / libxext6 / libxrender-dev → required by EasyOCR (OpenCV)
# libpq-dev                    → required by asyncpg / psycopg2 wheels
# Note: OpenJDK removed — code execution uses the Piston API (external),
#       so no local compiler is needed inside this container.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ──────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ────────────────────────────────────
COPY . .

# ── Health check ─────────────────────────────────────────────
# Render's default port is 10000; start-period is long because
# EasyOCR loads its model on first startup (~60 s).
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-10000}/health', timeout=5).raise_for_status()" || exit 1

# ── Expose port ──────────────────────────────────────────────
EXPOSE 10000

# ── Start command ────────────────────────────────────────────
# Render injects $PORT automatically (default 10000 on free tier).
# 1 worker is correct for free tier (512 MB RAM).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"]
