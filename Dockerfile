# Dockerfile for autobots-agents-jarvis
# Multi-stage build with Poetry
# Build context: autobots-agents-jarvis directory
# Usage: make docker-build
# Or: make docker-build-no-cache

# Stage 1: Builder - Install dependencies with Poetry
FROM python:3.12-slim-bookworm AS builder

# Install Poetry
ENV POETRY_VERSION=2.3.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without dev dependencies, without root package)
RUN poetry install --no-root --only main && \
    rm -rf $POETRY_CACHE_DIR

# Stage 2: Runtime
FROM python:3.12-slim-bookworm AS runtime

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1000 app && \
    useradd -u 1000 -g app -s /bin/bash -m app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Create directories for volume mounts with correct ownership
RUN mkdir -p configs && \
    chown -R app:app configs

# Copy application code (preserve src/ structure for PYTHONPATH)
COPY src ./src
COPY sbin ./sbin

# Change ownership to non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Activate virtual environment by adding to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose Chainlit port
EXPOSE 1337

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:1337/health || exit 1

# Run the Chainlit application
CMD ["bash", "sbin/run_jarvis.sh"]
