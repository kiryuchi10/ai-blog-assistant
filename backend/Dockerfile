# =========================================
# Base image
# =========================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# System dependencies:
# - build-essential & gcc: compile native extensions (if using psycopg2)
# - libpq-dev: PostgreSQL client headers (psycopg2 source build)
# - curl: for optional HEALTHCHECK
# - netcat-openbsd: optional readiness/wait scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverage Docker cache)
COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel \
 && python -m pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and own the app directory
# Use a stable UID/GID so mounted volumes don't break permissions
RUN groupadd -g 10001 app && useradd -m -u 10001 -g 10001 -s /bin/bash app \
 && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# (Optional) HEALTHCHECK to see if the app is up
# Requires 'curl' in the image; adjust URL if your health endpoint differs
HEALTHCHECK --interval=30s --timeout=3s --retries=5 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Default command:
# - For development: keep --reload (needs watchfiles in requirements.txt)
# - For production: use gunicorn (see below)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
