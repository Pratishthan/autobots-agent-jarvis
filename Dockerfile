# Dockerfile for autobots-agents-bro
# Multi-stage build
# Build context: autobots-agents-bro directory
# Usage: docker-compose up bro-chat
# Or: docker build -t autobots-agents-bro .

# Stage 1: Builder - Generate requirements from pyproject.toml
FROM python:3.12-slim-bookworm AS builder

# Set working directory
WORKDIR /build

# Copy only pyproject.toml to extract dependencies
COPY pyproject.toml .

# Generate requirements.txt from [project.dependencies]
# This will include autobots-devtools-shared-lib from PyPI
RUN echo "autobots-devtools-shared-lib==0.1.4a2" > requirements.txt && \
    echo "chainlit>=2.9.6" >> requirements.txt && \
    echo "langchain>=1.0.0" >> requirements.txt && \
    echo "langchain-google-genai>=4.2.0" >> requirements.txt && \
    echo "langfuse>=3.12.1" >> requirements.txt && \
    echo "pydantic-settings>=2.10.1" >> requirements.txt && \
    echo "python-dotenv>=1.1.1" >> requirements.txt && \
    echo "pyyaml>=6.0.3" >> requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim-bookworm AS runtime

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
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

# Create directories for volume mounts with correct ownership
RUN mkdir -p configs && \
    chown -R app:app configs

# Copy requirements from builder
COPY --from=builder /build/requirements.txt .

# Install all dependencies from PyPI (including autobots-devtools-shared-lib)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (preserve src/ structure for PYTHONPATH)
COPY src ./src
COPY sbin ./sbin

# Change ownership to non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose Chainlit port
EXPOSE 1337

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:1337/health || exit 1

# Run the Chainlit application
CMD ["bash", "sbin/run_jarvis.sh"]
