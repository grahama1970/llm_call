# LLM Call API Docker Container
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash llmcall

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY --chown=llmcall:llmcall pyproject.toml README.md ./

# Install uv for package management
RUN pip install --no-cache-dir uv

# Install Python dependencies (skip optional dev dependencies)
RUN sed -i '/rl-commons/d' pyproject.toml && \
    uv pip install --system --no-cache -e .

# Copy source code and config
COPY --chown=llmcall:llmcall src/ ./src/
COPY --chown=llmcall:llmcall config/ ./config/

# Copy entrypoint script
COPY --chown=llmcall:llmcall docker/api/entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/cache /app/.litellm && \
    chown -R llmcall:llmcall /app

# Switch to non-root user
USER llmcall

# Set environment variables
ENV PYTHONPATH=/app/src:/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Expose API port
EXPOSE 8001

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Use entrypoint script for initialization
ENTRYPOINT ["/app/entrypoint.sh"]