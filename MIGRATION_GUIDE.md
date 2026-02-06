# Migration Guide: pip to uv Docker Setup

This guide helps you migrate from the old pip-based Docker setup to the new uv-based multi-stage build.

## What Changed?

### Old Setup (pip)
- Single-stage Dockerfile
- pip with SSL workarounds (`--trusted-host`)
- Slow builds (5-10 minutes)
- Windows SSL issues
- requirements.txt (no lock file)

### New Setup (uv)
- Multi-stage Dockerfile (dev/prod)
- uv package manager (no SSL issues)
- Fast builds (1-3 minutes)
- Cross-platform compatibility
- uv.lock for deterministic builds
- Makefile for easy commands

## Migration Steps

### Step 1: Stop Old Containers

```bash
# Stop and remove old containers and volumes
docker-compose down -v

# Optional: Remove old images to free space
docker image rm searchmind-backend searchmind-frontend
```

### Step 2: Pull Latest Changes

```bash
git pull origin main  # or your branch
```

### Step 3: Verify New Files

Check that you have these new files:
```bash
ls -la | grep -E "(Makefile|docker-compose.prod.yml|DOCKER.md)"
```

Should show:
- `Makefile` ✓
- `docker-compose.prod.yml` ✓
- `DOCKER.md` ✓
- `QUICKSTART_DOCKER.md` ✓

### Step 4: Build New Setup

```bash
# Using Makefile (recommended)
make build

# Or using docker-compose directly
docker-compose build
```

**Expected time**: 1-3 minutes (first build)

### Step 5: Start Services

```bash
# Using Makefile
make up

# Or using docker-compose
docker-compose up -d
```

### Step 6: Verify Everything Works

```bash
# Check health
make health

# View logs
make logs-backend

# Test API
curl http://localhost:8000/health
```

### Step 7: Test Your Workflow

```bash
# Try the new commands
make help              # See all available commands
make logs-backend      # View backend logs
make shell-backend     # Open shell in backend
make restart-backend   # Restart backend
```

## Common Issues During Migration

### Issue: "uv: not found" error

**Solution**: Rebuild without cache
```bash
docker-compose build --no-cache backend
```

### Issue: Old containers still running

**Solution**: Force remove all containers
```bash
docker-compose down -v
docker ps -a  # Check no containers remain
make build
make up
```

### Issue: Port already in use

**Solution**: Kill old processes
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart
make up
```

### Issue: Models not downloading

**Solution**: Remove model cache
```bash
docker volume rm searchmind_backend-models
make restart-backend
```

### Issue: Permission denied on data directories

**Solution**: Fix permissions
```bash
# macOS/Linux
chmod -R 755 data/

# Windows: Run Docker Desktop as Administrator
```

## Command Migration Reference

| Old Command | New Command (Makefile) | Notes |
|-------------|------------------------|-------|
| `docker-compose build` | `make build` | Faster |
| `docker-compose up -d` | `make up` | Same |
| `docker-compose logs -f backend` | `make logs-backend` | Shorter |
| `docker-compose restart backend` | `make restart-backend` | Same |
| `docker-compose down` | `make down` | Same |
| `docker-compose exec backend bash` | `make shell-backend` | Shorter |
| `docker-compose down -v` | `make clean` | Clearer |

## Dockerfile Changes Reference

### Old Dockerfile (pip-based)
```dockerfile
FROM python:3.12-slim

# SSL workarounds for Windows
RUN pip config set global.trusted-host "pypi.org..."
RUN pip install --trusted-host pypi.org ...

# Long install times
RUN pip install --no-cache-dir --timeout=600 ...

COPY . .
CMD ["uvicorn", "app.main:app", "--reload"]
```

### New Dockerfile (uv-based)
```dockerfile
FROM python:3.12-slim AS base
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

FROM base AS dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen  # Fast, deterministic

FROM dependencies AS development
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--reload"]

FROM dependencies AS production
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--workers", "4"]
```

## Benefits You'll Notice

### 1. Speed
- **First build**: 1-3 min (vs 5-10 min)
- **Rebuild**: < 30 sec (vs 5-10 min)
- **Container start**: 5-10 sec (vs 10-20 sec)

### 2. Reliability
- ✅ No SSL certificate errors
- ✅ Deterministic builds with uv.lock
- ✅ Better error messages
- ✅ Windows compatibility

### 3. Developer Experience
- ✅ Simple commands: `make up`, `make logs`
- ✅ Clear command names: `make shell-backend`
- ✅ Fast rebuilds after code changes
- ✅ Separate dev/prod configurations

## Rollback (If Needed)

If you need to go back to the old setup:

```bash
# Stop new setup
make down

# Checkout old Dockerfile
git checkout HEAD~1 backend/Dockerfile

# Remove Makefile (optional)
rm Makefile

# Build old setup
docker-compose build
docker-compose up -d
```

**Note**: We don't recommend rolling back - the new setup is more reliable!

## Next Steps After Migration

1. **Read the quick start**: See `QUICKSTART_DOCKER.md`
2. **Learn Makefile commands**: Run `make help`
3. **Read detailed guide**: See `DOCKER.md`
4. **Update your team**: Share this migration guide
5. **Test on Windows**: Verify no SSL issues

## FAQ

### Q: Do I need to install uv on my machine?
**A**: No! uv is installed inside the Docker container. You only need Docker.

### Q: Can I still use docker-compose directly?
**A**: Yes! The Makefile just provides shortcuts. All docker-compose commands still work.

### Q: Will my data be lost?
**A**: No! The `data/` directory is mounted as a volume and persists across rebuilds.

### Q: What about my environment variables?
**A**: They're unchanged in `docker-compose.yml`. The new setup is compatible.

### Q: Can I use the old requirements.txt?
**A**: The new setup uses `pyproject.toml` and `uv.lock`. These are already in the repo.

### Q: What if I don't want to use Make?
**A**: You can still use `docker-compose` directly. The Makefile is optional but recommended.

## Testing Checklist

After migration, verify:

- [ ] Backend builds without errors
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can upload documents
- [ ] Can search documents
- [ ] Hot-reload works (edit a file, see change)
- [ ] Health check passes (`make health`)
- [ ] Tests run (`make test-backend`)
- [ ] Production build works (`make build-prod`)

## Support

If you encounter issues:

1. Check `DOCKER.md` for detailed troubleshooting
2. Try `make rebuild` (solves most issues)
3. Check logs with `make logs-backend`
4. Open an issue on GitHub with:
   - Error message
   - Output of `docker --version`
   - OS and version
   - Output of `make logs-backend`

---

**Welcome to the new Docker setup! 🎉**

Enjoy faster builds, better reliability, and a smoother development experience!
