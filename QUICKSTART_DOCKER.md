# Docker Quick Start - SearchMind

## 🚀 Get Started in 3 Commands

```bash
make build    # Build containers (first time: 1-3 min)
make up       # Start all services
make logs     # Watch the logs
```

**Done!** Access your app at:
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173
- API Docs: http://localhost:8000/docs

## 📋 Common Commands

### Daily Development Workflow
```bash
make up               # Start services
make logs-backend     # Watch backend logs
make restart-backend  # After code changes (if needed)
make down            # Stop everything
```

### Testing
```bash
make test-backend    # Run backend tests
make health          # Check if services are healthy
```

### Debugging
```bash
make shell-backend   # Open bash in backend container
make logs-backend    # View backend logs
make logs-frontend   # View frontend logs
```

### Clean Up
```bash
make down            # Stop containers
make clean           # Stop + remove volumes
make rebuild         # Full clean rebuild
```

### Production
```bash
make build-prod      # Build for production
make prod-up         # Start production mode
make prod-logs       # View production logs
make prod-down       # Stop production
```

## 🔧 Troubleshooting

### Container won't start?
```bash
make logs-backend    # Check what's wrong
make rebuild         # Nuclear option: rebuild everything
```

### Models not downloading?
```bash
docker volume rm searchmind_backend-models
make restart-backend
```

### Port already in use?
```bash
# Kill process using port 8000
lsof -i :8000        # Find process
kill -9 <PID>        # Kill it
make up              # Try again
```

### Hot-reload not working?
Make sure you're in development mode (default):
```bash
make down
make up              # Defaults to dev mode with hot-reload
```

## 📦 What's Installed?

The Docker setup includes:
- Python 3.12
- All ML models (FAISS, sentence-transformers, PaddleOCR)
- System dependencies (poppler, libgomp1)
- Development tools (pytest, httpx)

## 🎯 Benefits vs Old Setup

| Feature | Old (pip) | New (uv) |
|---------|-----------|----------|
| Build time | 5-10 min | 1-3 min |
| Rebuild time | 5-10 min | < 30 sec |
| Windows SSL issues | ❌ Common | ✅ Fixed |
| Deterministic builds | ❌ No | ✅ Yes |

## 💡 Pro Tips

1. **Always use `make` commands** - They're shorter and safer
2. **Watch logs while developing** - `make logs-backend` in a second terminal
3. **Don't edit inside containers** - Edit on your machine, hot-reload handles the rest
4. **Clean rebuild if weird issues** - `make rebuild` solves 90% of problems
5. **Check health before debugging** - `make health` shows what's actually running

## 🆘 Need More Help?

- **All commands**: `make help`
- **Detailed Docker guide**: See `DOCKER.md`
- **Full documentation**: See `README.md`

## ⚡ Power User Commands

```bash
# Execute any command in backend
make exec-backend CMD="uv run python -c 'import torch; print(torch.__version__)'"

# View last 50 log lines
docker-compose logs --tail=50 backend

# Rebuild just backend without cache
docker-compose build --no-cache backend

# Check container resource usage
docker stats searchmind-backend
```

---

**Remember**: First build takes 1-3 minutes, subsequent builds are < 30 seconds! ⚡
