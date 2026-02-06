# Docker Setup Guide

This document provides detailed information about the Docker setup for SearchMind.

## Architecture

The Docker setup uses a multi-stage build process with `uv` package manager for fast, reliable dependency installation.

### Multi-Stage Build

1. **base**: System dependencies and uv installation
2. **dependencies**: Python package installation (cached layer)
3. **development**: Development mode with hot-reload
4. **production**: Production mode with optimized workers

### Key Features

- **uv Package Manager**: 10-100x faster than pip, better cross-platform compatibility
- **Multi-stage Build**: Optimized caching and smaller images
- **Dev/Prod Modes**: Separate configurations for development and production
- **Volume Mounts**: Code hot-reload in development mode
- **Health Checks**: Automatic service health monitoring

## Directory Structure

```
searchmind/
├── backend/
│   ├── Dockerfile              # Multi-stage Dockerfile with uv
│   ├── pyproject.toml          # Python dependencies
│   ├── uv.lock                 # Locked dependency versions
│   └── .dockerignore           # Files to exclude from build
├── frontend/
│   └── Dockerfile              # Frontend container
├── docker-compose.yml          # Development configuration
├── docker-compose.prod.yml     # Production overrides
└── Makefile                    # Convenient Docker commands
```

## Build Process

### Development Build

```bash
# Using Makefile
make build

# Using docker-compose
docker-compose build

# Manual build
docker build \
  --target development \
  --build-arg INSTALL_DEV=true \
  -t searchmind-backend:dev \
  ./backend
```

### Production Build

```bash
# Using Makefile
make build-prod

# Using docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Manual build
docker build \
  --target production \
  --build-arg INSTALL_DEV=false \
  -t searchmind-backend:prod \
  ./backend
```

## Running Services

### Development Mode (Default)

Development mode includes:
- Hot-reload enabled (`--reload`)
- Code mounted as volume
- Dev dependencies installed
- Single worker process

```bash
# Start services
make up

# View logs
make logs-backend

# Restart after changes
make restart-backend
```

### Production Mode

Production mode includes:
- No hot-reload
- Optimized workers (4 workers)
- No dev dependencies
- Auto-restart on failure

```bash
# Start production services
make prod-up

# View production logs
make prod-logs

# Stop production services
make prod-down
```

## Volume Mounts

### Development Mode
- `./backend:/app` - Code hot-reload
- `./data:/app/data` - Persistent data storage
- `backend-models:/root/.cache` - ML model cache

### Production Mode
- `./data:/app/data` - Persistent data storage
- `backend-models:/root/.cache` - ML model cache

## Environment Variables

Configure via `docker-compose.yml` or `.env` file:

```bash
DATA_DIR=/app/data
UPLOAD_DIR=/app/data/uploads
INDEX_DIR=/app/data/faiss_index
TEMP_DIR=/app/data/temp
CHUNK_SIZE=400
CHUNK_OVERLAP=80
MAX_FILE_SIZE_MB=50
```

## Caching Strategy

The multi-stage build is optimized for caching:

1. **System packages** (apt-get) - Cached unless Dockerfile changes
2. **uv installation** - Cached unless Dockerfile changes
3. **Python dependencies** - Cached unless `pyproject.toml` or `uv.lock` changes
4. **Application code** - Rebuilt on every code change

This means most builds will be very fast (< 30 seconds) unless dependencies change.

## Dependency Management

### Adding New Dependencies

```bash
# 1. Add dependency to pyproject.toml
# 2. Update lock file
cd backend
uv sync

# 3. Rebuild Docker image
make rebuild
```

### Updating Dependencies

```bash
# Update all dependencies
cd backend
uv lock --upgrade

# Update specific package
uv lock --upgrade-package fastapi

# Rebuild Docker image
make rebuild
```

## Networking

Services communicate via `searchmind-network` bridge network:

- Backend: `http://backend:8000` (internal), `http://localhost:8000` (external)
- Frontend: `http://frontend:5173` (internal), `http://localhost:5173` (external)

## Health Checks

Backend includes a health check that:
- Runs every 30 seconds
- Times out after 10 seconds
- Retries 3 times before marking unhealthy
- Waits 40 seconds before starting checks

Check health status:
```bash
# Using Makefile
make health

# Using docker-compose
docker-compose ps
```

## Debugging

### View Logs

```bash
# All services
make logs

# Backend only
make logs-backend

# Frontend only
make logs-frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### Shell Access

```bash
# Open bash shell in backend
make shell-backend

# Execute single command
make exec-backend CMD="uv run python -c 'import torch; print(torch.__version__)'"
```

### Rebuild from Scratch

```bash
# Remove all containers, volumes, and rebuild
make rebuild

# Or manually
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Performance

### Build Times

- **First build**: 3-5 minutes (downloads all dependencies)
- **Rebuild with cache**: < 30 seconds (only code changes)
- **Dependency change**: 2-3 minutes (re-runs uv sync)

### Runtime Performance

- **Container startup**: 5-10 seconds
- **Model loading**: 10-20 seconds (first request)
- **Hot-reload**: < 1 second (development mode)

## Comparison: pip vs uv

| Aspect | pip (old) | uv (new) |
|--------|-----------|----------|
| Installation speed | 5-10 minutes | 1-3 minutes |
| SSL handling | Requires workarounds | Native support |
| Windows compatibility | Frequent issues | Excellent |
| Lock file support | Limited | Built-in |
| Caching | Basic | Advanced |
| Deterministic builds | Requires constraints.txt | Built-in with uv.lock |

## Troubleshooting

### Build fails with "uv: not found"

The uv installer script should add uv to PATH. If it fails:

```dockerfile
# Try manual installation in Dockerfile
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/
```

### Dependencies not installing

```bash
# Verify uv.lock is not in .dockerignore
cat backend/.dockerignore | grep uv.lock
# Should return nothing

# Try rebuilding without cache
docker-compose build --no-cache backend
```

### Container exits immediately

```bash
# Check logs for errors
make logs-backend

# Verify PYTHONPATH is correct
docker-compose exec backend uv run python -c "import app"
```

### Hot-reload not working

```bash
# Verify volume mount
docker-compose exec backend ls -la /app

# Check uvicorn is running with --reload
docker-compose exec backend ps aux | grep uvicorn
```

## Advanced Usage

### Custom Build Arguments

```bash
# Build with custom Python version
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --target development \
  ./backend

# Build with custom uv version
docker build \
  --build-arg UV_VERSION=0.1.0 \
  --target development \
  ./backend
```

### Multi-Platform Builds

```bash
# Build for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --target production \
  -t searchmind-backend:latest \
  ./backend
```

### CI/CD Integration

```bash
# Build for CI
docker-compose -f docker-compose.yml -f docker-compose.ci.yml build

# Run tests in CI
docker-compose run --rm backend uv run pytest --cov

# Build production image
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

## Security Considerations

1. **No Root User**: Consider adding non-root user in production
2. **Secrets Management**: Use Docker secrets or environment variables
3. **Network Isolation**: Use internal networks for service communication
4. **Resource Limits**: Set memory/CPU limits in docker-compose.yml
5. **Read-only Filesystem**: Consider making containers read-only where possible

## Additional Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)
