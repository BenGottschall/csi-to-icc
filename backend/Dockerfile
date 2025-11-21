# Backend Dockerfile for FastAPI application

# ============================================
# Base Stage - Common for dev and prod
# ============================================
FROM python:3.13-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ============================================
# Development Stage
# ============================================
FROM base as development

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with hot-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================
# Production Stage
# ============================================
FROM base as production

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Make start script executable
RUN chmod +x start.sh

# Switch to non-root user
USER appuser

# Expose port (Railway uses $PORT)
EXPOSE 8000

# Run application with migrations
CMD ["./start.sh"]
