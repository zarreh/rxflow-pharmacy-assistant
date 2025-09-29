# Production Dockerfile for RxFlow Pharmacy Assistant
# Multi-stage build for minimal final image
# Project: RxFlow Pharmacy Assistant - Isolated Build

# Build stage
FROM python:3.12-slim AS rxflow-builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set working directory
WORKDIR /app

# Copy Poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install only production dependencies
RUN poetry install --only=main --no-root --no-interaction --no-ansi

# Production stage - RxFlow Pharmacy Assistant
FROM python:3.12-slim AS rxflow-production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables specific to RxFlow
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    RXFLOW_APP=true \
    APP_NAME="RxFlow Pharmacy Assistant"

# Create non-root user for security
RUN groupadd -r rxflowuser && useradd -r -g rxflowuser rxflowuser

# Set working directory
WORKDIR /app

# Add labels for identification
LABEL maintainer="zarreh" \
      project="rxflow-pharmacy-assistant" \
      version="1.0.0" \
      description="RxFlow Pharmacy Assistant - AI-powered prescription refill system"

# Copy Python packages from builder stage
COPY --from=rxflow-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=rxflow-builder /usr/local/bin /usr/local/bin

# Copy application code
COPY rxflow/ ./rxflow/
COPY app.py .
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p /app/data/vector_store && \
    chown -R rxflowuser:rxflowuser /app

# Switch to non-root user
USER rxflowuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]