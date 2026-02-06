# =============================================================================
# Stage 1: Base - System dependencies and uv installation
# =============================================================================
FROM python:3.12-slim AS base

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgomp1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer (bypasses PyPI SSL issues)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.cargo/env && \
    uv --version

# Add uv to PATH for subsequent stages
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# =============================================================================
# Stage 2: Dependencies - Install Python packages
# =============================================================================
FROM base AS dependencies

# Copy dependency files for caching
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (frozen for deterministic builds)
# Use --no-dev for production, include dev deps for development
ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --frozen; \
    else \
        uv sync --frozen --no-dev; \
    fi

# =============================================================================
# Stage 3: Development - For local development with hot-reload
# =============================================================================
FROM dependencies AS development

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/faiss_index /app/data/temp

# Expose port
EXPOSE 8000

# Run with hot-reload for development
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# Stage 4: Production - Optimized for production deployment
# =============================================================================
FROM dependencies AS production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/uploads /app/data/faiss_index /app/data/temp

# Expose port
EXPOSE 8000

# Run without reload, with optimized settings
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
