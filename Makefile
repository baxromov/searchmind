.PHONY: help build build-prod build-backend build-frontend up down restart restart-backend restart-frontend logs logs-backend logs-frontend shell-backend exec-backend clean prune rebuild test-backend health prod-up prod-down prod-logs

# Default target
help:
	@echo "SearchMind Docker Management"
	@echo ""
	@echo "Build commands:"
	@echo "  make build              - Build all services (development mode)"
	@echo "  make build-prod         - Build all services (production mode)"
	@echo "  make build-backend      - Build backend only (development mode)"
	@echo "  make build-frontend     - Build frontend only"
	@echo ""
	@echo "Run commands:"
	@echo "  make up                 - Start all services in detached mode"
	@echo "  make down               - Stop and remove containers"
	@echo "  make restart            - Restart all services"
	@echo "  make restart-backend    - Restart backend only"
	@echo "  make restart-frontend   - Restart frontend only"
	@echo ""
	@echo "Development commands:"
	@echo "  make logs               - View logs from all services"
	@echo "  make logs-backend       - View backend logs only"
	@echo "  make logs-frontend      - View frontend logs only"
	@echo "  make shell-backend      - Open shell in backend container"
	@echo "  make exec-backend CMD=\"...\" - Execute command in backend container"
	@echo ""
	@echo "Maintenance commands:"
	@echo "  make clean              - Stop containers and remove volumes"
	@echo "  make prune              - Remove all unused Docker resources"
	@echo "  make rebuild            - Clean rebuild of all services"
	@echo ""
	@echo "Testing commands:"
	@echo "  make test-backend       - Run backend tests in container"
	@echo "  make health             - Check health of all services"
	@echo ""
	@echo "Production commands:"
	@echo "  make prod-up            - Start production mode"
	@echo "  make prod-down          - Stop production mode"
	@echo "  make prod-logs          - View production logs"

# Build commands
build:
	docker-compose build

build-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

build-backend:
	docker-compose build backend

build-frontend:
	docker-compose build frontend

# Run commands
up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

restart-backend:
	docker-compose restart backend

restart-frontend:
	docker-compose restart frontend

# Development commands
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

shell-backend:
	docker-compose exec backend /bin/bash

exec-backend:
	docker-compose exec backend $(CMD)

# Maintenance commands
clean:
	docker-compose down -v

prune:
	docker system prune -af --volumes

rebuild: clean build up

# Testing commands
test-backend:
	docker-compose exec backend uv run pytest

health:
	@echo "Checking backend health..."
	@curl -f http://localhost:8000/health || echo "Backend is not healthy"
	@echo "\nChecking frontend availability..."
	@curl -f http://localhost:5173 || echo "Frontend is not available"

# Production commands
prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
