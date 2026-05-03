# LokMat API — Multi-stage Docker build
# Per GEMINI.md: Cloud Run serverless container hosting
# Project: lokmat-495121

FROM python:3.12-slim AS base

# Security: non-root user
RUN groupadd -r lokmat && useradd -r -g lokmat lokmat

WORKDIR /app

# Install dependencies first (layer caching)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and migrations
COPY api/ ./api/
COPY alembic.ini .

# Security: switch to non-root user
USER lokmat

# Cloud Run uses PORT env var
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Health check for Cloud Run readiness probe
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:${PORT}/health'); r.raise_for_status()" || exit 1

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
