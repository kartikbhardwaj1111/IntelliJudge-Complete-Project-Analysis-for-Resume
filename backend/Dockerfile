# Multi-stage Dockerfile for IntelliJudge Backend
# Optimized for Railway deployment
# 
# Build stages:
# 1. base: Python runtime
# 2. builder: Install dependencies
# 3. runtime: Final image

FROM python:3.11-slim as runtime

# ── Metadata ────────────────────────────────────────────────
LABEL maintainer="IntelliJudge"
LABEL description="IntelliJudge Backend API — FastAPI + SQLAlchemy"

# ── Environment variables ──────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── System dependencies for building ───────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    # Required for EasyOCR
    libsm6 \
    libxext6 \
    libxrender-dev \
    # Required for some Python packages
    libpq-dev \
    # Compilers for local code execution
    g++ \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# ── Create working directory ───────────────────────────────
WORKDIR /app

# ── Copy requirements and install ──────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──────────────────────────────────
COPY . .

# ── Health check ───────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5).raise_for_status()" || exit 1

# ── Expose port ────────────────────────────────────────────
EXPOSE 8000

# ── Run the application ────────────────────────────────────
# Railway sets PORT environment variable automatically
# FastAPI will bind to 0.0.0.0:PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]