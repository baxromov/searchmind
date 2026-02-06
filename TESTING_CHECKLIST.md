# Testing Checklist for Docker Setup

Use this checklist to verify the Docker setup works correctly on your machine.

## Pre-Test Setup

- [ ] Docker Desktop is installed and running
- [ ] Docker Compose is available (`docker-compose --version`)
- [ ] Git repository is up to date (`git pull`)
- [ ] All old containers are stopped (`docker-compose down -v`)

## Basic Functionality Tests

### 1. Build Tests

- [ ] **Development build completes successfully**
  ```bash
  make build
  # Expected: Completes in 1-3 minutes without errors
  ```

- [ ] **Production build completes successfully**
  ```bash
  make build-prod
  # Expected: Completes in 1-3 minutes without SSL errors
  ```

- [ ] **Rebuild is fast**
  ```bash
  make rebuild
  # Expected: Completes in < 30 seconds (using cache)
  ```

### 2. Service Startup Tests

- [ ] **Backend starts successfully**
  ```bash
  make up
  make logs-backend
  # Expected: See "Application startup complete" message
  ```

- [ ] **Frontend starts successfully**
  ```bash
  make logs-frontend
  # Expected: See "Local: http://localhost:5173" message
  ```

- [ ] **Health check passes**
  ```bash
  make health
  # Expected: Both services return successful responses
  ```

### 3. API Functionality Tests

- [ ] **Backend health endpoint works**
  ```bash
  curl http://localhost:8000/health
  # Expected: {"status": "healthy"} or similar
  ```

- [ ] **API docs accessible**
  - Open http://localhost:8000/docs in browser
  - Expected: FastAPI documentation page loads

- [ ] **Frontend loads**
  - Open http://localhost:5173 in browser
  - Expected: SearchMind UI loads

### 4. Document Processing Tests

- [ ] **Can upload PDF document**
  - Navigate to http://localhost:5173
  - Upload a test PDF
  - Expected: Upload succeeds, processing completes

- [ ] **Can search documents**
  - Navigate to search page
  - Enter a query
  - Expected: Results returned with scores

- [ ] **FAISS index created**
  ```bash
  ls -la data/faiss_index/
  # Expected: See index files
  ```

### 5. Development Workflow Tests

- [ ] **Hot-reload works**
  ```bash
  make up
  # Edit backend/app/main.py (add a comment)
  make logs-backend
  # Expected: See "Detected file change, reloading" message
  ```

- [ ] **Volume mounts work**
  ```bash
  make shell-backend
  ls -la /app
  # Expected: See your source code files
  exit
  ```

- [ ] **Logs accessible**
  ```bash
  make logs-backend
  # Expected: See recent log output
  ```

### 6. Makefile Commands Test

- [ ] **make help works**
  ```bash
  make help
  # Expected: List of all commands
  ```

- [ ] **make restart-backend works**
  ```bash
  make restart-backend
  # Expected: Backend restarts quickly
  ```

- [ ] **make shell-backend works**
  ```bash
  make shell-backend
  # Expected: Bash prompt in container
  exit
  ```

- [ ] **make test-backend works**
  ```bash
  make test-backend
  # Expected: Tests run (may fail if no tests exist)
  ```

### 7. Production Mode Tests

- [ ] **Production build uses correct target**
  ```bash
  make build-prod
  docker inspect searchmind-backend | grep -i target
  # Expected: Shows "production" target
  ```

- [ ] **Production starts with multiple workers**
  ```bash
  make prod-up
  make prod-logs
  # Expected: See multiple worker processes
  ```

- [ ] **Production has no code volume mount**
  ```bash
  docker inspect searchmind-backend | grep Mounts -A 20
  # Expected: No /app mount, only /app/data
  ```

- [ ] **Production stops cleanly**
  ```bash
  make prod-down
  # Expected: Services stop without errors
  ```

### 8. Cleanup Tests

- [ ] **make down works**
  ```bash
  make down
  docker ps
  # Expected: No searchmind containers running
  ```

- [ ] **make clean works**
  ```bash
  make clean
  docker volume ls
  # Expected: searchmind volumes removed
  ```

## Performance Tests

- [ ] **First build time**
  ```bash
  time make build
  # Expected: 1-3 minutes on first build
  ```

- [ ] **Rebuild time (code change only)**
  ```bash
  touch backend/app/main.py
  time make build-backend
  # Expected: < 30 seconds
  ```

- [ ] **Container startup time**
  ```bash
  make down
  time make up
  # Expected: 5-10 seconds
  ```

- [ ] **Model loading time**
  ```bash
  make restart-backend
  time curl http://localhost:8000/health
  # Expected: 10-20 seconds for first request
  ```

## Cross-Platform Tests (Windows)

If testing on Windows:

- [ ] **Build completes without SSL errors**
  ```powershell
  make build
  # Expected: No "SSL certificate verify failed" errors
  ```

- [ ] **No trusted-host flags needed**
  ```bash
  cat backend/Dockerfile | grep trusted-host
  # Expected: No results (no SSL workarounds)
  ```

- [ ] **Path handling works correctly**
  ```bash
  make up
  make logs-backend
  # Expected: No path-related errors
  ```

## Error Recovery Tests

- [ ] **Recovery from failed build**
  ```bash
  # Intentionally break Dockerfile
  # Try to build
  # Fix Dockerfile
  make rebuild
  # Expected: Successful build after fix
  ```

- [ ] **Recovery from port conflict**
  ```bash
  # Start another service on port 8000
  make up
  # Expected: Clear error about port in use
  # Stop conflicting service
  make restart-backend
  # Expected: Successful restart
  ```

- [ ] **Recovery from corrupted cache**
  ```bash
  docker builder prune -af
  make rebuild
  # Expected: Successful rebuild
  ```

## Documentation Tests

- [ ] **README.md has Docker section**
  ```bash
  grep -i "docker" README.md
  # Expected: Multiple matches
  ```

- [ ] **DOCKER.md exists and is comprehensive**
  ```bash
  wc -l DOCKER.md
  # Expected: > 200 lines
  ```

- [ ] **All Makefile commands documented**
  ```bash
  make help
  # Expected: All commands have descriptions
  ```

## Final Validation

- [ ] All basic functionality tests passed
- [ ] All Makefile commands work
- [ ] Hot-reload works in development
- [ ] Production mode works correctly
- [ ] No SSL errors (especially on Windows)
- [ ] Build times are improved (< 3 min first build, < 30 sec rebuild)
- [ ] Documentation is clear and complete

## Test Results

**Date Tested**: _________________

**Tested By**: _________________

**Platform**:
- [ ] macOS
- [ ] Linux
- [ ] Windows

**Docker Version**: _________________

**Overall Result**:
- [ ] ✅ All tests passed
- [ ] ⚠️ Some tests passed with warnings
- [ ] ❌ Tests failed (see notes below)

**Notes**:
```
[Add any issues, warnings, or observations here]
```

## Common Issues and Solutions

### Issue: Build takes > 5 minutes
**Solution**: Check internet connection, consider pre-downloading models

### Issue: Container exits immediately
**Solution**: Check logs with `make logs-backend`, verify uv.lock not in .dockerignore

### Issue: Hot-reload not working
**Solution**: Verify in development mode, check volume mounts with `docker inspect`

### Issue: Port already in use
**Solution**: Kill conflicting process or change port in docker-compose.yml

### Issue: Models not downloading
**Solution**: Remove model cache: `docker volume rm searchmind_backend-models`

---

**After completing this checklist, your Docker setup is fully validated and ready for production use!**
