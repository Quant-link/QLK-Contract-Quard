# Backend Dockerfile for ContractQuard API - Updated for Railway PORT fix
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY web/backend/ ./web/backend/

# Copy and set up entrypoint script
COPY web/backend/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Set Python path
ENV PYTHONPATH=/app/src:/app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the application using entrypoint script
CMD ["./entrypoint.sh"]
